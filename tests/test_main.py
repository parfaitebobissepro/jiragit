import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append('../')
from src import *
from main import main

class TestMainMethods(unittest.TestCase):

    @patch('builtins.input', side_effect=['4'])
    @patch('builtins.print')
    def test_main_quit(self, mock_print, mock_input):
        with patch('src.GLOBAL_JSON_CONFIG', True):
            main()
            mock_print.assert_any_call("Au revoir !")

    @patch('builtins.input', side_effect=['1', '4'])
    @patch('builtins.print')
    @patch('main.start_new_task')
    def test_main_start_new_task(self, mock_start_new_task, mock_print, mock_input):
            mock_start_new_task.return_value = None  # Assure qu'elle ne fait rien
            main()  # Exécute main() avec les entrées simulées
            mock_start_new_task.assert_called_once() # Vérifie qu'elle a été appelée une fois

    @patch('builtins.input', side_effect=['2', '4'])
    @patch('builtins.print') 
    @patch('main.continue_development')  # Mock correctement la fonction continue_development
    def test_main_continue_development(self, mock_continue_development, mock_print, mock_input):
        mock_continue_development.return_value = None  # Empêche tout effet de bord
        main()  # Exécute main() avec les entrées simulées
        mock_continue_development.assert_called_once()  # Vérifie qu'elle a été appelée une fois

    @patch('builtins.input', side_effect=['3', '4'])
    @patch('builtins.print') 
    @patch('main.end_development')  # Mock correctement la fonction end_development
    def test_main_end_development(self, mock_end_development, mock_print, mock_input):
        mock_end_development.return_value = None  # Assure que la fonction ne fait rien
        main()  # Exécute main() avec les entrées simulées
        mock_end_development.assert_called_once()  # Vérifie qu'elle a été appelée une fois

    @patch('builtins.input', side_effect=['5', '4'])
    @patch('builtins.print')
    def test_main_invalid_choice(self, mock_print, mock_input):
        with patch('src.GLOBAL_JSON_CONFIG', True):
            main()
            mock_print.assert_any_call("Choix invalide. Veuillez réessayer.")

if __name__ == '__main__':
    unittest.main()