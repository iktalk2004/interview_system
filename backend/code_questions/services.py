import json
import subprocess
import time
import tempfile
import os
from typing import Dict, List, Any


class CodeExecutor:
    """
    代码执行器
    支持多种编程语言的代码执行和测试
    """

    def __init__(self):
        self.time_limit = 1000  # 默认时间限制（毫秒）
        self.memory_limit = 256  # 默认内存限制（MB）

    def execute(
        self,
        code: str,
        language: str,
        test_cases: List[Any],
        time_limit: int = 1000,
        memory_limit: int = 256
    ) -> Dict[str, Any]:
        """
        执行代码并运行测试用例

        Args:
            code: 用户提交的代码
            language: 编程语言
            test_cases: 测试用例列表
            time_limit: 时间限制（毫秒）
            memory_limit: 内存限制（MB）

        Returns:
            执行结果字典
        """
        self.time_limit = time_limit
        self.memory_limit = memory_limit

        results = []
        passed_count = 0
        total_runtime = 0
        max_memory = 0

        for test_case in test_cases:
            try:
                result = self._run_test_case(code, language, test_case)
                results.append(result)

                if result['passed']:
                    passed_count += 1

                total_runtime += result.get('runtime', 0)
                max_memory = max(max_memory, result.get('memory', 0))

                # 如果有测试用例失败，可以提前终止
                if not result['passed'] and result.get('error_type') in ['runtime_error', 'compile_error']:
                    break

            except Exception as e:
                results.append({
                    'test_case_id': test_case.id,
                    'passed': False,
                    'error': str(e),
                    'error_type': 'system_error'
                })

        # 确定整体状态
        if passed_count == len(test_cases):
            overall_status = 'accepted'
        elif any(r.get('error_type') == 'time_limit_exceeded' for r in results):
            overall_status = 'time_limit_exceeded'
        elif any(r.get('error_type') == 'memory_limit_exceeded' for r in results):
            overall_status = 'memory_limit_exceeded'
        elif any(r.get('error_type') == 'runtime_error' for r in results):
            overall_status = 'runtime_error'
        elif any(r.get('error_type') == 'compile_error' for r in results):
            overall_status = 'compile_error'
        elif passed_count == 0:
            overall_status = 'wrong_answer'
        else:
            overall_status = 'wrong_answer'

        return {
            'status': overall_status,
            'passed_test_cases': passed_count,
            'total_test_cases': len(test_cases),
            'runtime': total_runtime,
            'memory': max_memory,
            'test_case_results': results
        }

    def _run_test_case(
        self,
        code: str,
        language: str,
        test_case: Any
    ) -> Dict[str, Any]:
        """
        运行单个测试用例
        """
        input_data = json.loads(test_case.input_data)
        expected_output = json.loads(test_case.expected_output)

        # 根据语言执行代码
        if language == 'python':
            return self._run_python(code, input_data, expected_output)
        elif language == 'java':
            return self._run_java(code, input_data, expected_output)
        elif language == 'javascript':
            return self._run_javascript(code, input_data, expected_output)
        elif language == 'cpp':
            return self._run_cpp(code, input_data, expected_output)
        elif language == 'go':
            return self._run_go(code, input_data, expected_output)
        elif language == 'rust':
            return self._run_rust(code, input_data, expected_output)
        else:
            return {
                'test_case_id': test_case.id,
                'passed': False,
                'error': f'不支持的语言: {language}',
                'error_type': 'compile_error'
            }

    def _run_python(
        self,
        code: str,
        input_data: Any,
        expected_output: Any
    ) -> Dict[str, Any]:
        """
        执行 Python 代码
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            # 准备输入
            input_json = json.dumps(input_data)

            # 执行代码
            start_time = time.time()
            result = subprocess.run(
                ['python', temp_file],
                input=input_json,
                capture_output=True,
                text=True,
                timeout=self.time_limit / 1000
            )
            end_time = time.time()

            runtime = int((end_time - start_time) * 1000)

            # 清理临时文件
            os.unlink(temp_file)

            # 检查结果
            if result.returncode != 0:
                return {
                    'test_case_id': input_data.get('id', 0),
                    'passed': False,
                    'error': result.stderr,
                    'error_type': 'runtime_error',
                    'runtime': runtime
                }

            try:
                output = json.loads(result.stdout)
                passed = output == expected_output
            except json.JSONDecodeError:
                output = result.stdout.strip()
                passed = str(output) == str(expected_output)

            return {
                'test_case_id': input_data.get('id', 0),
                'passed': passed,
                'output': output,
                'expected_output': expected_output,
                'runtime': runtime,
                'memory': 0  # Python 难以准确测量内存
            }

        except subprocess.TimeoutExpired:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': '执行超时',
                'error_type': 'time_limit_exceeded',
                'runtime': self.time_limit
            }
        except Exception as e:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': str(e),
                'error_type': 'system_error'
            }

    def _run_java(
        self,
        code: str,
        input_data: Any,
        expected_output: Any
    ) -> Dict[str, Any]:
        """
        执行 Java 代码
        """
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 提取类名
                class_name = self._extract_java_class_name(code)
                if not class_name:
                    return {
                        'test_case_id': input_data.get('id', 0),
                        'passed': False,
                        'error': '无法找到 Java 类名',
                        'error_type': 'compile_error'
                    }

                # 写入 Java 文件
                java_file = os.path.join(temp_dir, f'{class_name}.java')
                with open(java_file, 'w') as f:
                    f.write(code)

                # 编译
                compile_result = subprocess.run(
                    ['javac', java_file],
                    capture_output=True,
                    text=True,
                    timeout=self.time_limit / 1000
                )

                if compile_result.returncode != 0:
                    return {
                        'test_case_id': input_data.get('id', 0),
                        'passed': False,
                        'error': compile_result.stderr,
                        'error_type': 'compile_error'
                    }

                # 运行
                input_json = json.dumps(input_data)
                start_time = time.time()
                run_result = subprocess.run(
                    ['java', '-cp', temp_dir, class_name],
                    input=input_json,
                    capture_output=True,
                    text=True,
                    timeout=self.time_limit / 1000
                )
                end_time = time.time()

                runtime = int((end_time - start_time) * 1000)

                # 检查结果
                if run_result.returncode != 0:
                    return {
                        'test_case_id': input_data.get('id', 0),
                        'passed': False,
                        'error': run_result.stderr,
                        'error_type': 'runtime_error',
                        'runtime': runtime
                    }

                try:
                    output = json.loads(run_result.stdout)
                    passed = output == expected_output
                except json.JSONDecodeError:
                    output = run_result.stdout.strip()
                    passed = str(output) == str(expected_output)

                return {
                    'test_case_id': input_data.get('id', 0),
                    'passed': passed,
                    'output': output,
                    'expected_output': expected_output,
                    'runtime': runtime,
                    'memory': 0
                }

        except subprocess.TimeoutExpired:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': '执行超时',
                'error_type': 'time_limit_exceeded',
                'runtime': self.time_limit
            }
        except Exception as e:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': str(e),
                'error_type': 'system_error'
            }

    def _run_javascript(
        self,
        code: str,
        input_data: Any,
        expected_output: Any
    ) -> Dict[str, Any]:
        """
        执行 JavaScript 代码
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                # 添加输入读取和输出逻辑
                full_code = f"""
{code}

const input = require('fs').readFileSync(0, 'utf-8');
const inputData = JSON.parse(input);
console.log(JSON.stringify(solution(inputData)));
"""
                f.write(full_code)
                temp_file = f.name

            # 准备输入
            input_json = json.dumps(input_data)

            # 执行代码
            start_time = time.time()
            result = subprocess.run(
                ['node', temp_file],
                input=input_json,
                capture_output=True,
                text=True,
                timeout=self.time_limit / 1000
            )
            end_time = time.time()

            runtime = int((end_time - start_time) * 1000)

            # 清理临时文件
            os.unlink(temp_file)

            # 检查结果
            if result.returncode != 0:
                return {
                    'test_case_id': input_data.get('id', 0),
                    'passed': False,
                    'error': result.stderr,
                    'error_type': 'runtime_error',
                    'runtime': runtime
                }

            try:
                output = json.loads(result.stdout)
                passed = output == expected_output
            except json.JSONDecodeError:
                output = result.stdout.strip()
                passed = str(output) == str(expected_output)

            return {
                'test_case_id': input_data.get('id', 0),
                'passed': passed,
                'output': output,
                'expected_output': expected_output,
                'runtime': runtime,
                'memory': 0
            }

        except subprocess.TimeoutExpired:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': '执行超时',
                'error_type': 'time_limit_exceeded',
                'runtime': self.time_limit
            }
        except Exception as e:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': str(e),
                'error_type': 'system_error'
            }

    def _run_cpp(
        self,
        code: str,
        input_data: Any,
        expected_output: Any
    ) -> Dict[str, Any]:
        """
        执行 C++ 代码
        """
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 写入 C++ 文件
                cpp_file = os.path.join(temp_dir, 'solution.cpp')
                with open(cpp_file, 'w') as f:
                    f.write(code)

                # 编译
                compile_result = subprocess.run(
                    ['g++', '-std=c++17', '-O2', cpp_file, '-o', os.path.join(temp_dir, 'solution')],
                    capture_output=True,
                    text=True,
                    timeout=self.time_limit / 1000
                )

                if compile_result.returncode != 0:
                    return {
                        'test_case_id': input_data.get('id', 0),
                        'passed': False,
                        'error': compile_result.stderr,
                        'error_type': 'compile_error'
                    }

                # 运行
                input_json = json.dumps(input_data)
                start_time = time.time()
                run_result = subprocess.run(
                    [os.path.join(temp_dir, 'solution')],
                    input=input_json,
                    capture_output=True,
                    text=True,
                    timeout=self.time_limit / 1000
                )
                end_time = time.time()

                runtime = int((end_time - start_time) * 1000)

                # 检查结果
                if run_result.returncode != 0:
                    return {
                        'test_case_id': input_data.get('id', 0),
                        'passed': False,
                        'error': run_result.stderr,
                        'error_type': 'runtime_error',
                        'runtime': runtime
                    }

                try:
                    output = json.loads(run_result.stdout)
                    passed = output == expected_output
                except json.JSONDecodeError:
                    output = run_result.stdout.strip()
                    passed = str(output) == str(expected_output)

                return {
                    'test_case_id': input_data.get('id', 0),
                    'passed': passed,
                    'output': output,
                    'expected_output': expected_output,
                    'runtime': runtime,
                    'memory': 0
                }

        except subprocess.TimeoutExpired:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': '执行超时',
                'error_type': 'time_limit_exceeded',
                'runtime': self.time_limit
            }
        except Exception as e:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': str(e),
                'error_type': 'system_error'
            }

    def _run_go(
        self,
        code: str,
        input_data: Any,
        expected_output: Any
    ) -> Dict[str, Any]:
        """
        执行 Go 代码
        """
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 写入 Go 文件
                go_file = os.path.join(temp_dir, 'main.go')
                with open(go_file, 'w') as f:
                    f.write(code)

                # 编译
                compile_result = subprocess.run(
                    ['go', 'build', '-o', os.path.join(temp_dir, 'main'), go_file],
                    capture_output=True,
                    text=True,
                    timeout=self.time_limit / 1000
                )

                if compile_result.returncode != 0:
                    return {
                        'test_case_id': input_data.get('id', 0),
                        'passed': False,
                        'error': compile_result.stderr,
                        'error_type': 'compile_error'
                    }

                # 运行
                input_json = json.dumps(input_data)
                start_time = time.time()
                run_result = subprocess.run(
                    [os.path.join(temp_dir, 'main')],
                    input=input_json,
                    capture_output=True,
                    text=True,
                    timeout=self.time_limit / 1000
                )
                end_time = time.time()

                runtime = int((end_time - start_time) * 1000)

                # 检查结果
                if run_result.returncode != 0:
                    return {
                        'test_case_id': input_data.get('id', 0),
                        'passed': False,
                        'error': run_result.stderr,
                        'error_type': 'runtime_error',
                        'runtime': runtime
                    }

                try:
                    output = json.loads(run_result.stdout)
                    passed = output == expected_output
                except json.JSONDecodeError:
                    output = run_result.stdout.strip()
                    passed = str(output) == str(expected_output)

                return {
                    'test_case_id': input_data.get('id', 0),
                    'passed': passed,
                    'output': output,
                    'expected_output': expected_output,
                    'runtime': runtime,
                    'memory': 0
                }

        except subprocess.TimeoutExpired:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': '执行超时',
                'error_type': 'time_limit_exceeded',
                'runtime': self.time_limit
            }
        except Exception as e:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': str(e),
                'error_type': 'system_error'
            }

    def _run_rust(
        self,
        code: str,
        input_data: Any,
        expected_output: Any
    ) -> Dict[str, Any]:
        """
        执行 Rust 代码
        """
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 写入 Rust 文件
                rust_file = os.path.join(temp_dir, 'main.rs')
                with open(rust_file, 'w') as f:
                    f.write(code)

                # 编译
                compile_result = subprocess.run(
                    ['rustc', rust_file, '-o', os.path.join(temp_dir, 'main')],
                    capture_output=True,
                    text=True,
                    timeout=self.time_limit / 1000
                )

                if compile_result.returncode != 0:
                    return {
                        'test_case_id': input_data.get('id', 0),
                        'passed': False,
                        'error': compile_result.stderr,
                        'error_type': 'compile_error'
                    }

                # 运行
                input_json = json.dumps(input_data)
                start_time = time.time()
                run_result = subprocess.run(
                    [os.path.join(temp_dir, 'main')],
                    input=input_json,
                    capture_output=True,
                    text=True,
                    timeout=self.time_limit / 1000
                )
                end_time = time.time()

                runtime = int((end_time - start_time) * 1000)

                # 检查结果
                if run_result.returncode != 0:
                    return {
                        'test_case_id': input_data.get('id', 0),
                        'passed': False,
                        'error': run_result.stderr,
                        'error_type': 'runtime_error',
                        'runtime': runtime
                    }

                try:
                    output = json.loads(run_result.stdout)
                    passed = output == expected_output
                except json.JSONDecodeError:
                    output = run_result.stdout.strip()
                    passed = str(output) == str(expected_output)

                return {
                    'test_case_id': input_data.get('id', 0),
                    'passed': passed,
                    'output': output,
                    'expected_output': expected_output,
                    'runtime': runtime,
                    'memory': 0
                }

        except subprocess.TimeoutExpired:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': '执行超时',
                'error_type': 'time_limit_exceeded',
                'runtime': self.time_limit
            }
        except Exception as e:
            return {
                'test_case_id': input_data.get('id', 0),
                'passed': False,
                'error': str(e),
                'error_type': 'system_error'
            }

    def _extract_java_class_name(self, code: str) -> str:
        """
        从 Java 代码中提取类名
        """
        import re
        match = re.search(r'public\s+class\s+(\w+)', code)
        if match:
            return match.group(1)
        return None
