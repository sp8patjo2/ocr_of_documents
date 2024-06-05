import unittest
from ocr import ocr_image

class TestOCR(unittest.TestCase):

    def test_ocr_helloworld(self):
        expected_text = "hello world"
        result_text = ocr_image("HelloWorld-easy.png")
        self.assertEqual(result_text.strip().lower(), expected_text)

if __name__ == '__main__':
    unittest.main()
