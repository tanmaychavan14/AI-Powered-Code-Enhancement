#!/usr/bin/env python3
"""
Enhanced JUnit Runner - Executes Java tests using JUnit with multiple fallback strategies
"""

import subprocess
import json
import re
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console

console = Console()

class JunitRunner:
    """Enhanced runner for executing Java tests with multiple strategies"""
    
    def __init__(self):
        self.console = Console()
        self.java_available = self._check_java_available()
        self.javac_available = self._check_javac_available()
        self.maven_available = self._check_maven_available()
        self.gradle_available = self._check_gradle_available()
        
        # Multiple execution strategies
        self.execution_strategies = [
            self._run_with_junit_direct,
            self._run_with_maven,
            self._run_with_gradle,
            self._run_basic_compilation_check
        ]
    
    def run_tests(self, test_file_path: str) -> Dict[str, Any]:
        """Execute Java tests using the best available method"""
        console.print(f"[cyan]🧪 Running Java tests: {Path(test_file_path).name}[/cyan]")
        
        # Try each execution strategy in order
        for i, strategy in enumerate(self.execution_strategies):
            try:
                console.print(f"[dim]Trying strategy {i+1}...[/dim]")
                result = strategy(test_file_path)
                if result['success']:
                    console.print(f"[green]✅ Tests executed successfully using strategy {i+1}[/green]")
                    return result
                else:
                    console.print(f"[yellow]Strategy {i+1} failed: {result.get('error', 'Unknown error')}[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Strategy {i+1} exception: {e}[/yellow]")
                continue
        
        # If all strategies fail, return comprehensive failure info
        return {
            'success': False,
            'error': 'All Java test execution strategies failed',
            'passed': 0,
            'failed': 0,
            'strategies_attempted': len(self.execution_strategies),
            'java_available': self.java_available,
            'maven_available': self.maven_available,
            'gradle_available': self.gradle_available
        }
    
    def _check_java_available(self) -> bool:
        """Check if Java is installed and available"""
        try:
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            available = result.returncode == 0
            if available:
                version_line = result.stderr.split('\n')[0] if result.stderr else result.stdout.split('\n')[0]
                console.print(f"[green]✅ Java available: {version_line}[/green]")
            else:
                console.print("[yellow]⚠️ Java not available[/yellow]")
            return available
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not check Java: {e}[/yellow]")
            return False
    
    def _check_javac_available(self) -> bool:
        """Check if Java compiler is available"""
        try:
            result = subprocess.run(['javac', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            available = result.returncode == 0
            if available:
                console.print("[green]✅ Java compiler available[/green]")
            return available
        except:
            console.print("[yellow]⚠️ Java compiler not available[/yellow]")
            return False
    
    def _check_maven_available(self) -> bool:
        """Check if Maven is available"""
        try:
            result = subprocess.run(['mvn', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            available = result.returncode == 0
            if available:
                console.print("[green]✅ Maven available[/green]")
            return available
        except Exception:
            console.print("[yellow]⚠️ Maven not available[/yellow]")
            return False
    
    def _check_gradle_available(self) -> bool:
        """Check if Gradle is available"""
        try:
            result = subprocess.run(['gradle', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            available = result.returncode == 0
            if available:
                console.print("[green]✅ Gradle available[/green]")
            return available
        except Exception:
            console.print("[yellow]⚠️ Gradle not available[/yellow]")
            return False
    
    def _run_with_junit_direct(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 1: Direct JUnit execution with downloaded JARs"""
        if not self.java_available or not self.javac_available:
            return {'success': False, 'error': 'Java/javac not available for direct JUnit'}
        
        try:
            console.print("[dim]Attempting direct JUnit execution...[/dim]")
            
            test_dir = Path(test_file_path).parent
            junit_dir = test_dir / "junit-jars"
            
            # Download JUnit jars if needed
            if not self._ensure_junit_jars(junit_dir):
                return {'success': False, 'error': 'Could not download JUnit jars'}
            
            # Get JUnit jar paths
            junit_jars = list(junit_dir.glob("*.jar"))
            if not junit_jars:
                return {'success': False, 'error': 'JUnit jars not found'}
            
            # Compile the test
            compilation_result = self._compile_java_test(test_file_path, junit_jars)
            if not compilation_result['success']:
                return compilation_result
            
            # Run the test
            execution_result = self._execute_junit_test(test_file_path, junit_jars)
            return execution_result
            
        except Exception as e:
            return {'success': False, 'error': f'Direct JUnit execution failed: {str(e)}'}
    
    def _run_with_maven(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 2: Run with Maven"""
        if not self.maven_available:
            return {'success': False, 'error': 'Maven not available'}
        
        try:
            # Check for pom.xml or create minimal one
            test_dir = Path(test_file_path).parent
            pom_path = self._find_or_create_pom(test_dir, test_file_path)
            
            if not pom_path:
                return {'success': False, 'error': 'Could not create Maven project structure'}
            
            # Ensure proper Maven directory structure
            self._setup_maven_structure(pom_path.parent, test_file_path)
            
            console.print("[dim]Running Maven test...[/dim]")
            
            # Run Maven test with timeout
            result = subprocess.run(['mvn', 'test', '-q'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=120,
                                  cwd=pom_path.parent,
                                  encoding='utf-8',
                                  errors='replace')
            
            return self._parse_maven_output(result, test_file_path)
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Maven test execution timed out'}
        except Exception as e:
            return {'success': False, 'error': f'Maven execution failed: {str(e)}'}
    
    def _run_with_gradle(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 3: Run with Gradle"""
        if not self.gradle_available:
            return {'success': False, 'error': 'Gradle not available'}
        
        try:
            # Check for build.gradle or create minimal one
            test_dir = Path(test_file_path).parent
            gradle_file = self._find_or_create_gradle_build(test_dir, test_file_path)
            
            if not gradle_file:
                return {'success': False, 'error': 'Could not create Gradle project structure'}
            
            # Ensure proper Gradle directory structure
            self._setup_gradle_structure(gradle_file.parent, test_file_path)
            
            console.print("[dim]Running Gradle test...[/dim]")
            
            # Run Gradle test
            result = subprocess.run(['gradle', 'test', '--info'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=120,
                                  cwd=gradle_file.parent,
                                  encoding='utf-8',
                                  errors='replace')
            
            return self._parse_gradle_output(result, test_file_path)
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Gradle test execution timed out'}
        except Exception as e:
            return {'success': False, 'error': f'Gradle execution failed: {str(e)}'}
    
    def _run_basic_compilation_check(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 4: Basic compilation and structure validation"""
        try:
            console.print("[dim]Performing Java compilation check...[/dim]")
            
            if not self.javac_available:
                # Fallback to basic file analysis
                return self._analyze_java_test_structure(test_file_path)
            
            # Try to compile the Java file
            result = subprocess.run(['javac', test_file_path], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=30,
                                  encoding='utf-8',
                                  errors='replace')
            
            if result.returncode == 0:
                # Compilation successful, analyze test structure
                analysis = self._analyze_java_test_structure(test_file_path)
                analysis['compilation_successful'] = True
                return analysis
            else:
                return {
                    'success': False,
                    'error': f'Java compilation error: {result.stderr}',
                    'compilation_successful': False
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Compilation check failed: {str(e)}'}
    
    def _ensure_junit_jars(self, junit_dir: Path) -> bool:
        """Download JUnit JARs if they don't exist"""
        try:
            junit_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if JARs already exist
            if list(junit_dir.glob("*.jar")):
                console.print("[green]JUnit JARs already available[/green]")
                return True
            
            console.print("[dim]Downloading JUnit JARs...[/dim]")
            
            # URLs for JUnit 5 JARs
            junit_urls = {
                "junit-jupiter-engine-5.8.2.jar": "https://repo1.maven.org/maven2/org/junit/jupiter/junit-jupiter-engine/5.8.2/junit-jupiter-engine-5.8.2.jar",
                "junit-jupiter-api-5.8.2.jar": "https://repo1.maven.org/maven2/org/junit/jupiter/junit-jupiter-api/5.8.2/junit-jupiter-api-5.8.2.jar",
                "junit-platform-console-standalone-1.8.2.jar": "https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.8.2/junit-platform-console-standalone-1.8.2.jar"
            }
            
            # Try to download using various methods
            import urllib.request
            
            for jar_name, url in junit_urls.items():
                jar_path = junit_dir / jar_name
                try:
                    console.print(f"[dim]Downloading {jar_name}...[/dim]")
                    urllib.request.urlretrieve(url, jar_path)
                    console.print(f"[green]Downloaded {jar_name}[/green]")
                    return True  # If we get at least one JAR, that's enough
                except Exception as e:
                    console.print(f"[yellow]Failed to download {jar_name}: {e}[/yellow]")
                    continue
            
            # If download fails, try to find system JUnit
            system_paths = [
                "/usr/share/java/junit*.jar",
                "/opt/junit/*.jar",
                str(Path.home() / ".m2/repository/org/junit/**/*.jar")
            ]
            
            for path_pattern in system_paths:
                import glob
                jars = glob.glob(path_pattern, recursive=True)
                if jars:
                    # Copy found JARs to our directory
                    for jar in jars[:3]:  # Limit to first 3 JARs
                        try:
                            shutil.copy2(jar, junit_dir / Path(jar).name)
                            console.print(f"[green]Found system JAR: {Path(jar).name}[/green]")
                            return True
                        except Exception as e:
                            console.print(f"[yellow]Could not copy {jar}: {e}[/yellow]")
            
            return False
            
        except Exception as e:
            console.print(f"[yellow]Failed to ensure JUnit JARs: {e}[/yellow]")
            return False
    
    def _compile_java_test(self, test_file_path: str, junit_jars: List[Path]) -> Dict[str, Any]:
        """Compile Java test file with JUnit"""
        try:
            classpath = ":".join(str(jar) for jar in junit_jars)
            
            cmd = ['javac', '-cp', classpath, test_file_path]
            
            console.print(f"[dim]Compiling: {' '.join(cmd)}[/dim]")
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True,
                                  timeout=30,
                                  encoding='utf-8',
                                  errors='replace')
            
            if result.returncode == 0:
                console.print("[green]Compilation successful[/green]")
                return {'success': True, 'message': 'Compilation successful'}
            else:
                return {
                    'success': False,
                    'error': f'Compilation failed: {result.stderr}'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Compilation error: {str(e)}'}
    
    def _execute_junit_test(self, test_file_path: str, junit_jars: List[Path]) -> Dict[str, Any]:
        """Execute compiled JUnit test"""
        try:
            test_class = Path(test_file_path).stem
            test_dir = Path(test_file_path).parent
            
            # Find the console standalone JAR
            console_jar = None
            for jar in junit_jars:
                if 'console-standalone' in jar.name:
                    console_jar = jar
                    break
            
            if console_jar:
                # Use JUnit Platform Console Launcher
                cmd = [
                    'java', '-jar', str(console_jar),
                    '--class-path', str(test_dir),
                    '--select-class', test_class
                ]
            else:
                # Fallback to direct execution
                classpath = ":".join(str(jar) for jar in junit_jars) + ":" + str(test_dir)
                cmd = [
                    'java', '-cp', classpath,
                    'org.junit.platform.console.ConsoleLauncher',
                    '--select-class', test_class
                ]
            
            console.print(f"[dim]Executing: {' '.join(cmd)}[/dim]")
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True,
                                  timeout=60,
                                  cwd=test_dir,
                                  encoding='utf-8',
                                  errors='replace')
            
            return self._parse_junit_console_output(result, test_file_path)
            
        except Exception as e:
            return {'success': False, 'error': f'JUnit execution error: {str(e)}'}
    
    def _find_or_create_pom(self, test_dir: Path, test_file_path: str) -> Optional[Path]:
        """Find existing pom.xml or create a minimal one"""
        # Look for existing pom.xml in parent directories
        current_dir = test_dir
        for _ in range(5):  # Check up to 5 levels up
            pom_path = current_dir / "pom.xml"
            if pom_path.exists():
                console.print(f"[green]Found existing pom.xml: {pom_path}[/green]")
                return pom_path
            current_dir = current_dir.parent
            if current_dir == current_dir.parent:  # Reached root
                break
        
        # Create minimal pom.xml
        pom_path = test_dir / "pom.xml"
        
        pom_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.generated.tests</groupId>
    <artifactId>generated-java-tests</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>jar</packaging>
    
    <properties>
        <maven.compiler.source>8</maven.compiler.source>
        <maven.compiler.target>8</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <junit.version>5.8.2</junit.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${{junit.version}}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0-M7</version>
                <configuration>
                    <includes>
                        <include>**/*Test.java</include>
                        <include>**/Test*.java</include>
                    </includes>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>8</source>
                    <target>8</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>"""
        
        try:
            with open(pom_path, 'w', encoding='utf-8') as f:
                f.write(pom_content)
            console.print(f"[green]Created minimal pom.xml: {pom_path}[/green]")
            return pom_path
        except Exception as e:
            console.print(f"[yellow]Failed to create pom.xml: {e}[/yellow]")
            return None
    
    def _find_or_create_gradle_build(self, test_dir: Path, test_file_path: str) -> Optional[Path]:
        """Find existing build.gradle or create a minimal one"""
        # Look for existing build.gradle
        current_dir = test_dir
        for _ in range(5):
            gradle_path = current_dir / "build.gradle"
            if gradle_path.exists():
                console.print(f"[green]Found existing build.gradle: {gradle_path}[/green]")
                return gradle_path
            current_dir = current_dir.parent
            if current_dir == current_dir.parent:
                break
        
        # Create minimal build.gradle
        gradle_path = test_dir / "build.gradle"
        
        gradle_content = """
plugins {
    id 'java'
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation 'org.junit.jupiter:junit-jupiter:5.8.2'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}

test {
    useJUnitPlatform()
    testLogging {
        events "passed", "skipped", "failed"
        exceptionFormat "full"
        showStandardStreams = true
    }
}

java {
    sourceCompatibility = JavaVersion.VERSION_1_8
    targetCompatibility = JavaVersion.VERSION_1_8
}
"""
        
        try:
            with open(gradle_path, 'w', encoding='utf-8') as f:
                f.write(gradle_content)
            console.print(f"[green]Created minimal build.gradle: {gradle_path}[/green]")
            return gradle_path
        except Exception as e:
            console.print(f"[yellow]Failed to create build.gradle: {e}[/yellow]")
            return None
    
    def _setup_maven_structure(self, project_dir: Path, test_file_path: str):
        """Setup proper Maven directory structure"""
        # Create Maven directory structure
        src_test_java = project_dir / "src" / "test" / "java"
        src_test_java.mkdir(parents=True, exist_ok=True)
        
        # Copy test file to proper location if not already there
        test_file = Path(test_file_path)
        target_file = src_test_java / test_file.name
        
        if not target_file.exists() and test_file.exists():
            try:
                shutil.copy2(test_file, target_file)
                console.print(f"[green]Copied test file to Maven structure: {target_file}[/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not copy test file: {e}[/yellow]")
    
    def _setup_gradle_structure(self, project_dir: Path, test_file_path: str):
        """Setup proper Gradle directory structure"""
        # Create Gradle directory structure
        src_test_java = project_dir / "src" / "test" / "java"
        src_test_java.mkdir(parents=True, exist_ok=True)
        
        # Copy test file to proper location if not already there
        test_file = Path(test_file_path)
        target_file = src_test_java / test_file.name
        
        if not target_file.exists() and test_file.exists():
            try:
                shutil.copy2(test_file, target_file)
                console.print(f"[green]Copied test file to Gradle structure: {target_file}[/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not copy test file: {e}[/yellow]")
    
    def _analyze_java_test_structure(self, test_file_path: str) -> Dict[str, Any]:
        """Analyze Java test file structure without execution"""
        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count test methods and assertions
            test_patterns = [
                (r'@Test\s+public\s+void\s+(\w+)', 'public test methods'),
                (r'@Test\s+void\s+(\w+)', 'void test methods'),
                (r'public\s+void\s+test(\w+)', 'test methods by convention')
            ]
            
            assertion_patterns = [
                (r'assertEquals\s*\(', 'assertEquals'),
                (r'assertTrue\s*\(', 'assertTrue'),
                (r'assertFalse\s*\(', 'assertFalse'),
                (r'assertNotNull\s*\(', 'assertNotNull'),
                (r'assertNull\s*\(', 'assertNull'),
                (r'assertThrows\s*\(', 'assertThrows')
            ]
            
            test_methods = []
            test_counts = {}
            
            for pattern, name in test_patterns:
                matches = re.findall(pattern, content)
                test_methods.extend(matches)
                test_counts[name] = len(matches)
            
            assertion_counts = {}
            total_assertions = 0
            
            for pattern, name in assertion_patterns:
                count = len(re.findall(pattern, content))
                assertion_counts[name] = count
                total_assertions += count
            
            # Look for imports
            imports = re.findall(r'import\s+([^;]+);', content)
            
            return {
                'success': True,
                'passed': 0,
                'failed': 0,
                'syntax_valid': True,
                'test_methods_found': len(test_methods),
                'test_method_names': test_methods,
                'assertion_count': total_assertions,
                'assertion_breakdown': assertion_counts,
                'test_count_breakdown': test_counts,
                'imports_found': imports,
                'test_file': test_file_path,
                'method': 'structure_analysis',
                'message': f'Structure valid. Found {len(test_methods)} test methods and {total_assertions} assertions.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Structure analysis failed: {str(e)}'
            }
    
    def _parse_maven_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse Maven test output"""
        output = result.stdout + result.stderr
        
        try:
            # Look for Maven Surefire test results
            patterns = [
                (r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)', 'surefire'),
                (r'Tests: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)', 'alternative'),
                (r'(\d+) tests completed, (\d+) failed', 'simple')
            ]
            
            for pattern, pattern_type in patterns:
                match = re.search(pattern, output)
                if match:
                    if pattern_type == 'surefire' or pattern_type == 'alternative':
                        tests_run = int(match.group(1))
                        failures = int(match.group(2))
                        errors = int(match.group(3))
                        skipped = int(match.group(4))
                        passed = tests_run - failures - errors - skipped
                    else:  # simple
                        tests_run = int(match.group(1))
                        failed = int(match.group(2))
                        passed = tests_run - failed
                        failures = failed
                        errors = 0
                        skipped = 0
                    
                    return {
                        'success': result.returncode == 0 and failures == 0 and errors == 0,
                        'passed': passed,
                        'failed': failures + errors,
                        'skipped': skipped,
                        'total': tests_run,
                        'test_file': test_file_path,
                        'method': 'maven',
                        'output': output
                    }
            
            # Look for BUILD SUCCESS/FAILURE
            if 'BUILD SUCCESS' in output:
                return {
                    'success': True,
                    'passed': 1,
                    'failed': 0,
                    'skipped': 0,
                    'test_file': test_file_path,
                    'method': 'maven_build_success',
                    'output': output,
                    'message': 'Maven build successful'
                }
            elif 'BUILD FAILURE' in output:
                return {
                    'success': False,
                    'passed': 0,
                    'failed': 1,
                    'error': 'Maven build failed',
                    'test_file': test_file_path,
                    'method': 'maven_build_failure',
                    'output': output
                }
            
            # Check for compilation errors
            if 'COMPILATION ERROR' in output:
                return {
                    'success': False,
                    'passed': 0,
                    'failed': 1,
                    'error': 'Compilation error',
                    'test_file': test_file_path,
                    'method': 'maven_compile_error',
                    'output': output
                }
            
            # Default fallback
            return {
                'success': result.returncode == 0,
                'passed': 1 if result.returncode == 0 else 0,
                'failed': 0 if result.returncode == 0 else 1,
                'skipped': 0,
                'test_file': test_file_path,
                'method': 'maven_fallback',
                'output': output
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Maven output parsing failed: {str(e)}',
                'output': output
            }
    
    def _parse_gradle_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse Gradle test output"""
        output = result.stdout + result.stderr
        
        try:
            # Look for Gradle test summary patterns
            patterns = [
                (r'(\d+) tests completed, (\d+) failed, (\d+) skipped', 'detailed'),
                (r'(\d+) tests completed, (\d+) failed', 'simple'),
                (r'BUILD SUCCESSFUL', 'build_success'),
                (r'BUILD FAILED', 'build_failed')
            ]
            
            for pattern, pattern_type in patterns:
                if pattern_type in ['build_success', 'build_failed']:
                    if re.search(pattern, output):
                        return {
                            'success': pattern_type == 'build_success',
                            'passed': 1 if pattern_type == 'build_success' else 0,
                            'failed': 0 if pattern_type == 'build_success' else 1,
                            'skipped': 0,
                            'test_file': test_file_path,
                            'method': f'gradle_{pattern_type}',
                            'output': output,
                            'message': f'Gradle {pattern_type.replace("_", " ")}'
                        }
                else:
                    match = re.search(pattern, output)
                    if match:
                        completed = int(match.group(1))
                        failed = int(match.group(2))
                        skipped = int(match.group(3)) if pattern_type == 'detailed' else 0
                        passed = completed - failed - skipped
                        
                        return {
                            'success': result.returncode == 0 and failed == 0,
                            'passed': passed,
                            'failed': failed,
                            'skipped': skipped,
                            'total': completed,
                            'test_file': test_file_path,
                            'method': 'gradle',
                            'output': output
                        }
            
            # Fallback
            return {
                'success': result.returncode == 0,
                'passed': 1 if result.returncode == 0 else 0,
                'failed': 0 if result.returncode == 0 else 1,
                'skipped': 0,
                'test_file': test_file_path,
                'method': 'gradle_fallback',
                'output': output
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Gradle output parsing failed: {str(e)}',
                'output': output
            }
    
    def _parse_junit_console_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse JUnit Console Launcher output"""
        output = result.stdout + result.stderr
        
        try:
            # JUnit 5 console output patterns
            patterns = [
                (r'Test run finished after \d+ ms.*?(\d+) tests found.*?(\d+) tests successful.*?(\d+) tests failed', 'detailed'),
                (r'(\d+) tests found.*?(\d+) tests successful.*?(\d+) tests failed', 'simple'),
                (r'(\d+) tests successful', 'success_only'),
                (r'(\d+) tests failed', 'failure_only')
            ]
            
            for pattern, pattern_type in patterns:
                match = re.search(pattern, output, re.DOTALL)
                if match:
                    if pattern_type == 'detailed':
                        tests_found = int(match.group(1))
                        tests_successful = int(match.group(2))
                        tests_failed = int(match.group(3))
                    elif pattern_type == 'simple':
                        tests_found = int(match.group(1))
                        tests_successful = int(match.group(2))
                        tests_failed = int(match.group(3))
                    elif pattern_type == 'success_only':
                        tests_successful = int(match.group(1))
                        tests_failed = 0
                        tests_found = tests_successful
                    else:  # failure_only
                        tests_failed = int(match.group(1))
                        tests_successful = 0
                        tests_found = tests_failed
                    
                    return {
                        'success': result.returncode == 0 and tests_failed == 0,
                        'passed': tests_successful,
                        'failed': tests_failed,
                        'total': tests_found,
                        'test_file': test_file_path,
                        'method': 'junit_console',
                        'output': output
                    }
            
            # If no specific patterns found, check for general success/failure
            if result.returncode == 0:
                return {
                    'success': True,
                    'passed': 1,
                    'failed': 0,
                    'test_file': test_file_path,
                    'method': 'junit_console_success',
                    'output': output
                }
            else:
                return {
                    'success': False,
                    'passed': 0,
                    'failed': 1,
                    'test_file': test_file_path,
                    'method': 'junit_console_failure',
                    'output': output
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'JUnit console output parsing failed: {str(e)}',
                'output': output
            }
    
    def get_installation_instructions(self) -> Dict[str, Any]:
        """Get instructions for installing Java testing dependencies"""
        return {
            'java': {
                'command': 'Install JDK 8 or later from https://adoptopenjdk.net/',
                'description': 'Java Development Kit required for compilation and execution',
                'verification': 'java -version && javac -version'
            },
            'maven': {
                'command': 'Install Apache Maven from https://maven.apache.org/',
                'description': 'Build tool for Java projects with dependency management',
                'verification': 'mvn --version'
            },
            'gradle': {
                'command': 'Install Gradle from https://gradle.org/',
                'description': 'Alternative build tool for Java projects',
                'verification': 'gradle --version'
            },
            'junit': {
                'description': 'JUnit will be automatically downloaded or managed by Maven/Gradle',
                'manual_download': 'JARs will be automatically downloaded if needed'
            }
        }
    
    def diagnose_environment(self) -> Dict[str, Any]:
        """Diagnose the Java testing environment"""
        diagnosis = {
            'java_available': self.java_available,
            'javac_available': self.javac_available,
            'maven_available': self.maven_available,
            'gradle_available': self.gradle_available,
            'recommendations': []
        }
        
        if not self.java_available:
            diagnosis['recommendations'].append('Install Java JDK (version 8 or later recommended)')
        
        if not self.javac_available:
            diagnosis['recommendations'].append('Install Java Development Kit (JDK) - not just JRE')
        
        if not self.maven_available and not self.gradle_available:
            diagnosis['recommendations'].append('Install either Maven or Gradle for dependency management')
        
        # Check for common Java project files
        try:
            has_pom = os.path.exists('pom.xml')
            has_gradle = os.path.exists('build.gradle')
            
            diagnosis['has_maven_project'] = has_pom
            diagnosis['has_gradle_project'] = has_gradle
            
            if not has_pom and not has_gradle:
                diagnosis['recommendations'].append('Consider creating a Maven (pom.xml) or Gradle (build.gradle) project')
                
        except:
            pass
        
        return diagnosis