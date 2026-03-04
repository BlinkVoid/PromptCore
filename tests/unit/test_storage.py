from datetime import datetime
from promptcore.persistence import ReasoningLogCreate, ReasoningLog

class TestStorage:
    def test_create_log(self, in_memory_storage):
        log_data = ReasoningLogCreate(
            task_input="Test task",
            context="Test context",
            detected_category="code",
            complexity_score=5.5,
            selected_framework="chain_of_thought",
            meta_prompt_generated="Prompt content"
        )
        
        log = in_memory_storage.create_log(log_data)
        
        assert log.id is not None
        assert isinstance(log.timestamp, datetime)
        assert log.task_input == "Test task"
        
        # Verify persistence
        fetched = in_memory_storage.get_log(log.id)
        assert fetched is not None
        assert fetched.id == log.id

    def test_update_feedback(self, in_memory_storage):
        # Create log
        log_data = ReasoningLogCreate(
            task_input="Test",
            detected_category="general",
            complexity_score=1.0,
            selected_framework="default",
            meta_prompt_generated="prompt"
        )
        log = in_memory_storage.create_log(log_data)
        
        # Update feedback
        updated = in_memory_storage.update_feedback(log.id, "Good result")
        
        assert updated is not None
        assert updated.execution_feedback == "Good result"
        
        # Verify persistence
        fetched = in_memory_storage.get_log(log.id)
        assert fetched.execution_feedback == "Good result"

    def test_get_stats(self, in_memory_storage):
        # Initial stats
        stats = in_memory_storage.get_stats()
        assert stats["total_logs"] == 0
        
        # Add a log
        in_memory_storage.create_log(ReasoningLogCreate(
            task_input="t1",
            detected_category="code",
            complexity_score=5.0,
            selected_framework="framework_a",
            meta_prompt_generated="p1"
        ))
        
        # Check stats
        stats = in_memory_storage.get_stats()
        assert stats["total_logs"] == 1
        assert stats["by_category"]["code"] == 1
        assert stats["by_framework"]["framework_a"] == 1
        assert stats["average_complexity"] == 5.0
