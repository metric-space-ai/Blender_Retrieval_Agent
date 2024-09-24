import re
from enum import StrEnum
import base64


def check_dict(template_dict: dict, test_dict: dict):
    if (
        template_dict.keys() == dict.keys()
    ):  # Check if the same keys are shared between dicts
        for key in test_dict.keys():
            if (
                test_dict[key].type == template_dict[key]
            ):  # Check if tested dict types are correct
                continue
            else:
                if template_dict[key].type == StrEnum:  # Special check for StrEnum
                    if (
                        test_dict[key] in test_dict[key]
                    ):  # Check if str is part of StrEnum
                        return True
                    else:
                        return False
                else:
                    return False
    else:
        return False


def embed_file_to_base_64(file_path):
    print(f"Embeding {file_path} to base 64 string")

    # Read file content
    with open(file_path, "rb") as file:
        file_byte_array = file.read()

    # Convert the content to bytes, then encode to Base64
    base64_bytes = base64.b64encode(file_byte_array).decode("utf-8")

    return base64_bytes


def try_to_run_code(code_string):
    """Tries to run gpt generated code and returns error string if failed"""
    try:
        exec(code_string, globals())
        print("Generated code passed and is executed")
        return
    except Exception as e:
        print(f"Generated code failed and gave exception: {e}")
        return str(e)


def static_code_check(code_string):
    """Performs a series of static checks for potential issues."""
    issues = []

    imports = re.findall(r"[^#]*import [^\n#]+", code_string)
    if imports:
        issues.append("Code contains import statements: " + ", ".join(imports))

    system_calls = re.findall(r"[^#]*(os\.system|subprocess\.[^\n#]+)", code_string)
    if system_calls:
        issues.append(
            "Code contains os.system or subprocess calls: " + ", ".join(system_calls)
        )

    operations = re.findall(
        r"[^#]*(open\(|write\(|delete\(|read\()[^\n#]+", code_string
    )
    if operations:
        issues.append("Code contains file operations: " + ", ".join(operations))

    access = re.findall(r"[^#]*(os\.getenv|os\.environ)[^\n#]+", code_string)
    if access:
        issues.append("Code accesses environment variables: " + ", ".join(access))

    ctypes_calls = re.findall(r"[^#]*ctypes[^\n#]+", code_string)
    if ctypes_calls:
        issues.append(
            "Code contains calls to ctypes functions: " + ", ".join(ctypes_calls)
        )

    pickles = re.findall(
        r"[^#]*(pickle\.load|pickle\.loads|pickle\.dump|pickle\.dumps)[^\n#]+",
        code_string,
    )
    if pickles:
        issues.append("Code contains pickling/unpickling: " + ", ".join(pickles))

    dangerous_functions = re.findall(r"[^#]*(eval\(|exec\()[^\n#]+", code_string)
    if dangerous_functions:
        issues.append(
            "Code contains dangerous functions like eval() or exec(): "
            + ", ".join(dangerous_functions)
        )

    if issues:
        print("Generated code failed static check")
        return "\n".join(issues)
    else:
        print("Generated code passed static check")
        return
