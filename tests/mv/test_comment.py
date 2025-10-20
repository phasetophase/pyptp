"""Tests for TCommentMS class."""

from __future__ import annotations

import unittest

from pyptp.elements.mv.comment import CommentMV
from pyptp.elements.mv.shared import Comment
from pyptp.network_mv import NetworkMV


class TestTCommentMS(unittest.TestCase):
    """Test TCommentMS registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkMV()

    def test_comment_registration_works(self) -> None:
        """Verify basic comment registration in network."""
        comment = CommentMV(comment=Comment(text="Test comment"))

        # Verify network starts empty
        self.assertEqual(len(self.network.comments), 0)

        # Register comment
        comment.register(self.network)

        # Verify comment was added
        self.assertEqual(len(self.network.comments), 1)
        self.assertEqual(self.network.comments[0], comment)

    def test_comment_with_text_serializes_correctly(self) -> None:
        """Test serialization with comment text."""
        comment = CommentMV(comment=Comment(text="This is a test comment"))

        result = comment.serialize()
        expected = "#Comment Text:'This is a test comment'"

        self.assertEqual(result, expected)

    def test_comment_with_empty_text_serializes_correctly(self) -> None:
        """Test serialization with empty comment text."""
        comment = CommentMV(comment=Comment(text=""))

        result = comment.serialize()
        expected = "#Comment "

        self.assertEqual(result, expected)

    def test_comment_with_special_characters_serializes_correctly(self) -> None:
        """Test serialization with special characters in comment text."""
        comment = CommentMV(comment=Comment(text="Test with 'quotes' and symbols!@#$%"))

        result = comment.serialize()
        expected = "#Comment Text:'Test with 'quotes' and symbols!@#$%'"

        self.assertEqual(result, expected)

    def test_comment_deserialization_works(self) -> None:
        """Test deserialization from VNF format data."""
        data = {"comment": [{"Text": "Deserialized comment"}]}

        comment = CommentMV.deserialize(data)

        self.assertEqual(comment.comment.text, "Deserialized comment")

    def test_comment_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        comment = CommentMV.deserialize(data)

        self.assertEqual(comment.comment.text, "")

    def test_comment_deserialization_with_capital_text_key(self) -> None:
        """Test deserialization with capital Text key."""
        data = {"comment": [{"Text": "Comment with capital key"}]}

        comment = CommentMV.deserialize(data)

        self.assertEqual(comment.comment.text, "Comment with capital key")

    def test_comment_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_text = "Round trip test comment"
        comment = CommentMV(comment=Comment(text=original_text))

        # Serialize
        serialized = comment.serialize()

        # Simulate parsing back from VNF format
        # Note: This is a simplified test since actual VNF parsing is more complex
        data = {"comment": [{"Text": original_text}]}

        deserialized = CommentMV.deserialize(data)

        self.assertEqual(deserialized.comment.text, original_text)
        self.assertEqual(deserialized.serialize(), serialized)

    def test_multiple_comments_registration(self) -> None:
        """Test registering multiple comments in network."""
        comment1 = CommentMV(comment=Comment(text="First comment"))
        comment2 = CommentMV(comment=Comment(text="Second comment"))
        comment3 = CommentMV(comment=Comment(text="Third comment"))

        # Register all comments
        comment1.register(self.network)
        comment2.register(self.network)
        comment3.register(self.network)

        # Verify all comments are in network
        self.assertEqual(len(self.network.comments), 3)
        self.assertEqual(self.network.comments[0].comment.text, "First comment")
        self.assertEqual(self.network.comments[1].comment.text, "Second comment")
        self.assertEqual(self.network.comments[2].comment.text, "Third comment")

    def test_comment_shared_class_serialize(self) -> None:
        """Test the Comment shared class serialization."""
        comment = Comment(text="Shared class test")

        result = comment.serialize()
        expected = "Text:Shared class test"

        self.assertEqual(result, expected)

    def test_comment_shared_class_deserialize(self) -> None:
        """Test the Comment shared class deserialization."""
        data = {"Text": "Shared deserialize test"}

        comment = Comment.deserialize(data)

        self.assertEqual(comment.text, "Shared deserialize test")

    def test_comment_shared_class_deserialize_with_capital_key(self) -> None:
        """Test the Comment shared class deserialization with capital Text key."""
        data = {"Text": "Capital key test"}

        comment = Comment.deserialize(data)

        self.assertEqual(comment.text, "Capital key test")


if __name__ == "__main__":
    unittest.main()
