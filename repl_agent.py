import io
import json
import os
import sys
import tempfile
import time

from openai import OpenAI

REPL_SYSTEM_PROMPT = """You are tasked with answering a query with associated context. You can access, transform, and analyze this context interactively in a REPL environment that can recursively query sub-LLMs, which you are strongly encouraged to use as much as possible. You will be queried iteratively until you provide a final answer.

The REPL environment is initialized with:
1. A `context` variable that contains extremely important information about your query. You should check the content of the `context` variable to understand what you are working with. Make sure you look through it sufficiently as you answer your query.
2. The ability to use `print()` statements to view the output of your REPL code and continue your reasoning.

Make sure to explicitly look through the entire context in REPL before answering your query. You can use the REPL environment to help you understand your context. Think step by step carefully, plan, and execute this plan immediately in your response. Remember to explicitly answer the original query in your final answer."""


class REPLAgent:
    def __init__(self, model="gpt-4o-mini", setup_code=None):
        self.client = OpenAI()
        self.model = model
        # Initialize state with restricted built-ins for security
        self.state = {
            "__name__": "__main__",  # Required for class definitions
            "__builtins__": {
                # Safe built-ins for string manipulation
                "print": print,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "bool": bool,
                "type": type,
                "isinstance": isinstance,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sorted": sorted,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "round": round,
                "chr": chr,
                "ord": ord,
                "hex": hex,
                "bin": bin,
                "oct": oct,
                "repr": repr,
                "ascii": ascii,
                "format": format,
                "__import__": __import__,  # Allow imports
                "__build_class__": __build_class__,  # Allow class definitions
                "open": open,  # Allow file access
                # Add commonly used built-ins that were missing
                "any": any,
                "all": all,
                "hasattr": hasattr,
                "getattr": getattr,
                "setattr": setattr,
                "delattr": delattr,
                "dir": dir,
                "vars": vars,
                "range": range,  # Add range function
                "reversed": reversed,  # Add reversed function
                "slice": slice,  # Add slice function
                "iter": iter,  # Add iter function
                "next": next,  # Add next function
                "pow": pow,  # Add pow function
                "divmod": divmod,  # Add divmod function
                "complex": complex,  # Add complex function
                "bytes": bytes,  # Add bytes function
                "bytearray": bytearray,  # Add bytearray function
                "memoryview": memoryview,  # Add memoryview function
                "hash": hash,  # Add hash function
                "id": id,  # Add id function
                "callable": callable,  # Add callable function
                "issubclass": issubclass,  # Add issubclass function
                "super": super,  # Add super function
                "property": property,  # Add property function
                "staticmethod": staticmethod,  # Add staticmethod function
                "classmethod": classmethod,  # Add classmethod function
                "object": object,  # Add object class
                # Add exception classes
                "Exception": Exception,
                "ValueError": ValueError,
                "TypeError": TypeError,
                "KeyError": KeyError,
                "IndexError": IndexError,
                "AttributeError": AttributeError,
                "FileNotFoundError": FileNotFoundError,
                "OSError": OSError,
                "IOError": IOError,
                "RuntimeError": RuntimeError,
                "NameError": NameError,
                "ImportError": ImportError,
                "StopIteration": StopIteration,
                "GeneratorExit": GeneratorExit,
                "SystemExit": SystemExit,
                "KeyboardInterrupt": KeyboardInterrupt,
                "BaseException": BaseException,
                "ArithmeticError": ArithmeticError,
                "LookupError": LookupError,
                "AssertionError": AssertionError,
                "NotImplementedError": NotImplementedError,
                "UnicodeError": UnicodeError,
                "Warning": Warning,
                "UserWarning": UserWarning,
                "DeprecationWarning": DeprecationWarning,
                "SyntaxWarning": SyntaxWarning,
                "RuntimeWarning": RuntimeWarning,
                "FutureWarning": FutureWarning,
                "ImportWarning": ImportWarning,
                "UnicodeWarning": UnicodeWarning,
                "BytesWarning": BytesWarning,
                "ResourceWarning": ResourceWarning,
                "ZeroDivisionError": ZeroDivisionError,
                "SyntaxError": SyntaxError,
                # Block dangerous built-ins
                "input": None,  # Block input
                "eval": None,  # Block eval
                "exec": None,  # Block exec
                "compile": None,  # Block compile
                "globals": None,  # Block globals access
                "locals": None,  # Block locals access
            },
        }
        self.temp_dir = tempfile.mkdtemp(prefix="repl_agent_")
        self.last_messages = []
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "python_exec",
                    "description": "Execute Python code in a stateful REPL environment. Previously defined variables and imports remain available across calls.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The Python code to execute",
                            }
                        },
                        "required": ["code"],
                    },
                },
            }
        ]

        # Run setup code if provided
        if setup_code:
            self.run(setup_code)

    def __del__(self):
        """Clean up temporary directory when object is destroyed."""
        try:
            import shutil

            shutil.rmtree(self.temp_dir)
        except:
            pass

    def load_context(self, context_json=None, context_str=None):
        if context_json is not None:
            path = os.path.join(self.temp_dir, "context.json")
            with open(path, "w") as f:
                json.dump(context_json, f)
            self.run(
                f"import json\nwith open(r'{path}') as f:\n    context = json.load(f)"
            )
        elif context_str is not None:
            path = os.path.join(self.temp_dir, "context.txt")
            with open(path, "w") as f:
                f.write(context_str)
            self.run(f"with open(r'{path}') as f:\n    context = f.read()")

    def run(self, code):
        start = time.time()
        old_cwd, old_stdout, old_stderr = os.getcwd(), sys.stdout, sys.stderr
        stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
        sys.stdout, sys.stderr = stdout_buf, stderr_buf

        try:
            os.chdir(self.temp_dir)
            lines = code.split("\n")
            # Only extract top-level imports (not indented), as indented imports
            # are part of control flow structures like try/except
            imports = [
                l
                for l in lines
                if l.strip().startswith(("import ", "from "))
                and not l.strip().startswith("#")
                and not l.startswith((" ", "\t"))  # Not indented
            ]
            others = [l for l in lines if l not in imports]

            if imports:
                exec("\n".join(imports), self.state)

            if others:
                non_empty = [
                    l for l in others if l.strip() and not l.strip().startswith("#")
                ]
                if non_empty:
                    last = non_empty[-1].strip()
                    is_expr = (
                        not last.startswith(
                            (
                                "import ",
                                "from ",
                                "def ",
                                "class ",
                                "if ",
                                "for ",
                                "while ",
                                "try:",
                                "with ",
                                "return ",
                                "yield ",
                                "break",
                                "continue",
                                "pass",
                                "raise",
                                "print(",
                            )
                        )
                        and "=" not in last.split("#")[0]
                        and not last.endswith(":")
                    )

                    if is_expr:
                        try:
                            idx = next(
                                i
                                for i in range(len(others) - 1, -1, -1)
                                if others[i].strip() == last
                            )
                            if idx > 0:
                                exec("\n".join(others[:idx]), self.state)
                            result = eval(last, self.state)
                            if result is not None:
                                print(repr(result))
                        except:
                            exec("\n".join(others), self.state)
                    else:
                        exec("\n".join(others), self.state)
                elif others:
                    exec("\n".join(others), self.state)

            output, error = stdout_buf.getvalue(), stderr_buf.getvalue()
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}" if str(e) else type(e).__name__
            output, error = stdout_buf.getvalue(), stderr_buf.getvalue() or error_msg
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr
            os.chdir(old_cwd)

        # Save stdout and stderr to state for access
        self.state["_stdout"] = output
        self.state["_stderr"] = error

        vars_list = [
            k for k in self.state if not k.startswith("_") and k != "__builtins__"
        ]
        if vars_list and not error:
            output += f"\n[Variables: {', '.join(vars_list)}]"
        if not error:
            output += f"\n[Execution: {time.time() - start:.3f}s]"
        if len(output) > 2000:
            output = output[:2000] + f"\n... (truncated {len(output) - 2000} chars)"

        return (
            f"{output}Error: {error}"
            if error and output
            else f"Error: {error}"
            if error
            else output
        )

    def chat(self, user_message, max_iterations=10, verbose=False):
        messages = [
            {"role": "system", "content": REPL_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        for i in range(max_iterations):
            if verbose:
                print(f"\n[Iteration {i + 1}]")
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, tools=self.tools
            )
            msg = response.choices[0].message
            if msg.tool_calls:
                if verbose:
                    print(f"Tool calls: {len(msg.tool_calls)}")
                messages.append(
                    {
                        "role": "assistant",
                        "content": msg.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in msg.tool_calls
                        ],
                    }
                )
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments)
                    if verbose:
                        print(
                            f"  Calling {tc.function.name}\n  Code:\n{args.get('code', '')}\n"
                        )
                    result = (
                        self.run(args["code"])
                        if tc.function.name == "python_exec"
                        else f"Error: Unknown function {tc.function.name}"
                    )
                    if verbose:
                        print(f"  Result:\n{result}\n")
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": tc.function.name,
                            "content": result or "(No output)",
                        }
                    )
            else:
                if verbose:
                    print("Final response received")
                self.last_messages = messages
                return msg.content
        self.last_messages = messages
        return "Max iterations reached. The model may need more steps to complete the task."

    def get_tool_calls(self):
        calls = []
        for msg in self.last_messages:
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    calls.append(
                        {
                            "id": tc["id"],
                            "function": tc["function"]["name"],
                            "arguments": json.loads(tc["function"]["arguments"]),
                        }
                    )
        return calls

    def print_tool_calls(self):
        calls = self.get_tool_calls()
        if not calls:
            print("No tool calls found in last chat session.")
            return
        print(f"\n{'=' * 80}\nTool Calls ({len(calls)} total)\n{'=' * 80}")
        for i, tc in enumerate(calls, 1):
            print(f"\n[{i}] {tc['function']}\nID: {tc['id']}")
            if tc["function"] == "python_exec" and "code" in tc["arguments"]:
                print(f"Code:\n{tc['arguments']['code']}")
            else:
                print(f"Arguments: {tc['arguments']}")
        print("=" * 80)
