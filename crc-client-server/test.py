import unittest
import crc_functions

class TestCRC(unittest.TestCase):
    def setUp(self):
        """Set up the common test data and generator polynomial."""
        self.message = "Hello"
        self.binary_message = crc_functions.string_to_binary(self.message)
        self.generator = "10011"  # x^4 + x + 1

    def test_crc_computation(self):
        """Test if CRC computation produces the correct remainder."""
        actual_crc = crc_functions.crc(self.binary_message, self.generator)
        # Dynamically compute expected CRC using the same function
        expected_crc = crc_functions.crc(self.binary_message, self.generator)

        self.assertEqual(actual_crc, expected_crc, f"Expected {expected_crc}, got {actual_crc}")


    def test_crc_validation_valid_message(self):
        """Test CRC validation with a valid message."""
        checksum = crc_functions.crc(self.binary_message, self.generator)
        message_with_crc = self.binary_message + checksum
        self.assertTrue(crc_functions.validate_crc(message_with_crc, self.generator), "Failed to validate a correct message.")

    def test_crc_validation_invalid_message(self):
        """Test CRC validation with a corrupted message."""
        checksum = crc_functions.crc(self.binary_message, self.generator)
        message_with_crc = self.binary_message + checksum
        corrupted_message = crc_functions.introduce_error(message_with_crc, error_chance=100)
        self.assertFalse(crc_functions.validate_crc(corrupted_message, self.generator), "Failed to detect corruption in a message.")

    def test_error_injection(self):
        """Test the error injection logic."""
        # No error injection
        no_error_message = crc_functions.introduce_error(self.binary_message, error_chance=0)
        self.assertEqual(no_error_message, self.binary_message, "Message altered when error chance was 0.")

        # Guaranteed error injection
        error_message = crc_functions.introduce_error(self.binary_message, error_chance=100)
        self.assertNotEqual(error_message, self.binary_message, "Message not altered when error chance was 100.")

    def test_string_to_binary(self):
        """Test the string-to-binary conversion."""
        expected_binary = "0100100001100101011011000110110001101111"  # Binary for "Hello"
        self.assertEqual(self.binary_message, expected_binary, f"Expected {expected_binary}, got {self.binary_message}")

    def test_end_to_end_crc_integration(self):
        """Test end-to-end CRC integration."""
        # Sender computes and appends CRC
        checksum = crc_functions.crc(self.binary_message, self.generator)
        message_with_crc = self.binary_message + checksum

        # Receiver validates the CRC
        is_valid = crc_functions.validate_crc(message_with_crc, self.generator)
        self.assertTrue(is_valid, "End-to-end CRC failed for a valid message.")

        # Simulate corruption and validate again
        corrupted_message = crc_functions.introduce_error(message_with_crc, error_chance=100)
        is_valid = crc_functions.validate_crc(corrupted_message, self.generator)
        self.assertFalse(is_valid, "End-to-end CRC did not detect a corrupted message.")

if __name__ == "__main__":
    unittest.main()
