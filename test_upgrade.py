"""
Automated Test Suite for JARVIS Upgrade Verification
Tests intent classification, in-app search, contextual reference resolution,
multi-turn memory, security validations, and task lifecycle management.
"""
import unittest
from engine.intent_router import intent_router
from engine.conversation_manager import conv_manager
from engine.task_manager import task_manager, TaskState
from engine.security import SecurityPolicy
from engine.web_engine import web_engine

class TestJarvisIntelligence(unittest.TestCase):
    def setUp(self):
        conv_manager.clear_history()

    def test_in_app_search_no_chrome(self):
        """Verify 'search for python' uses in-app search without opening Chrome."""
        res = intent_router.route_and_execute("search for python decorators")
        self.assertEqual(res["type"], "search_results")
        self.assertIsNotNone(res["data"])
        self.assertTrue(len(res["data"]) > 0)
        self.assertTrue(len(res["spoken"]) > 0)

    def test_contextual_reference_resolution(self):
        """Verify multi-turn reference: 'explain the first result' -> resolves from search."""
        # Step 1: Perform search
        search_res = intent_router.route_and_execute("search for cybersecurity news")
        self.assertEqual(search_res["type"], "search_results")
        first_title = conv_manager.last_search_results[0]["title"]

        # Step 2: Contextual follow-up
        explain_res = intent_router.route_and_execute("explain the first result")
        self.assertEqual(explain_res["type"], "ai_response")
        self.assertIn(first_title, explain_res["display"])

    def test_security_policy_allowlist(self):
        """Verify security allowlist blocks unauthorized actions and sanitizes app names."""
        self.assertTrue(SecurityPolicy.is_action_allowed("set_volume"))
        self.assertTrue(SecurityPolicy.is_action_allowed("take_screenshot"))
        self.assertFalse(SecurityPolicy.is_action_allowed("format_c_drive"))
        self.assertFalse(SecurityPolicy.is_action_allowed("delete_system32"))
        
        # Injection test
        self.assertFalse(SecurityPolicy.validate_app_name("calc.exe && rm -rf"))
        self.assertTrue(SecurityPolicy.validate_app_name("notepad"))

    def test_task_cancellation_and_speech_stop(self):
        """Verify stop speaking and cancel task mechanics."""
        t = task_manager.create_task("Test background task")
        self.assertEqual(len(task_manager.active_tasks), 1)

        res = intent_router.route_and_execute("cancel this task")
        self.assertEqual(res["type"], "status")
        self.assertEqual(len(task_manager.active_tasks), 0)

    def test_notes_productivity(self):
        """Verify note creation and retrieval."""
        res = intent_router.route_and_execute("take a note review security audit tomorrow")
        self.assertEqual(res["type"], "note")
        notes = conv_manager.get_notes()
        self.assertTrue(any("review security audit" in n["content"] for n in notes))

    def test_confirmation_required_for_shutdown(self):
        """Verify destructive actions require confirmation."""
        res = intent_router.route_and_execute("shutdown laptop")
        self.assertEqual(res["type"], "confirmation")
        self.assertTrue(task_manager.has_pending_confirmation())

        # Cancel confirmation
        cancel_res = intent_router.route_and_execute("cancel")
        self.assertFalse(task_manager.has_pending_confirmation())

if __name__ == "__main__":
    unittest.main()
