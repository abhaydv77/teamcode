from teamcode.domain.message import Message


class TestMessage:
    def test_create_text_message(self) -> None:
        msg = Message(id="msg-1", sender="alice", content="Hello")
        assert msg.sender == "alice"
        assert msg.recipient is None
        assert msg.message_type == "text"
