"""
Test coverage for main.py __main__ block execution
This file specifically targets lines 418-423 and 426-427 in main.py
"""
import subprocess
import sys
import tempfile
import os
from unittest.mock import patch, Mock


class TestMainBlockCoverage:
    """Test coverage of main.py __main__ execution block"""
    
    def test_main_block_execution_via_subprocess(self):
        """Test __main__ block by executing main.py as subprocess"""
        # Create a temporary script that imports and executes main with __name__ == "__main__"
        test_script = '''
import sys
import os
sys.path.insert(0, os.getcwd())

# Mock uvicorn to avoid actual server startup
from unittest.mock import patch, Mock
with patch('uvicorn.run') as mock_run:
    # Execute main.py content with __name__ == "__main__"
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    # Execute with __name__ set to "__main__"
    exec_globals = {'__name__': '__main__', '__file__': 'main.py'}
    exec(main_content, exec_globals)
    
    # Verify uvicorn.run was called
    assert mock_run.called, "uvicorn.run should have been called"
    args, kwargs = mock_run.call_args
    assert args[0] == "main:app"
    assert kwargs.get('host') == "0.0.0.0"
    assert kwargs.get('port') == 8000
    assert kwargs.get('reload') == True
    
print("SUCCESS: __main__ block executed and tested")
'''
        
        # Write test script to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            temp_script = f.name
        
        try:
            # Execute the test script
            result = subprocess.run(
                [sys.executable, temp_script],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.getcwd()
            )
            
            # Check if execution was successful
            assert result.returncode == 0, f"Script failed: {result.stderr}"
            assert "SUCCESS" in result.stdout, f"Test failed: {result.stdout}"
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_script):
                os.unlink(temp_script)
    
    def test_main_block_direct_import_simulation(self):
        """Test __main__ block by simulating direct import"""
        with patch('uvicorn.run') as mock_uvicorn:
            # Read main.py and execute it with __name__ == "__main__"
            with open('main.py', 'r') as f:
                main_code = f.read()
            
            # Create execution environment
            exec_globals = {
                '__name__': '__main__',
                '__file__': 'main.py',
                '__builtins__': __builtins__
            }
            
            # Execute the main.py code
            exec(main_code, exec_globals)
            
            # Verify uvicorn.run was called with correct parameters
            mock_uvicorn.assert_called_once_with(
                "main:app",
                host="0.0.0.0", 
                port=8000,
                reload=True
            )
    
    def test_main_conditional_logic(self):
        """Test the conditional logic of the __main__ block"""
        # Test that the condition __name__ == "__main__" works correctly
        
        # When __name__ is not "__main__", uvicorn should not be called
        with patch('uvicorn.run') as mock_uvicorn:
            exec_globals = {'__name__': 'not_main'}
            
            # This should not trigger uvicorn.run
            code = '''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''
            exec(code, exec_globals)
            mock_uvicorn.assert_not_called()
        
        # When __name__ is "__main__", uvicorn should be called
        with patch('uvicorn.run') as mock_uvicorn:
            exec_globals = {'__name__': '__main__'}
            
            code = '''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''
            exec(code, exec_globals)
            mock_uvicorn.assert_called_once_with(
                "main:app", host="0.0.0.0", port=8000, reload=True
            ) 