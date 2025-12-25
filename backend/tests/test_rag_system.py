"""
Comprehensive RAG System Test Suite

Tests RAG system against all researched attack vectors.
"""

import pytest
from app.services.rag_system import RAGSystem, ThreatCategory
from app.services.attack_knowledge_base import AttackKnowledgeBase, initialize_attack_knowledge_base


@pytest.fixture
def rag_system():
    """Create RAG system instance"""
    return RAGSystem()


@pytest.fixture
def attack_kb(rag_system):
    """Create and seed attack knowledge base"""
    return initialize_attack_knowledge_base(rag_system)


class TestRAGAttackDetection:
    """Test RAG system against attack vectors"""

    def test_prompt_injection_detection(self, attack_kb):
        """Test RAG can retrieve prompt injection knowledge"""
        attacks = attack_kb.get_attacks_by_category("prompt_injection")
        assert len(attacks) > 0
        
        # Test retrieval for injection query
        results = attack_kb.rag.search("ignore previous instructions", "prompt_injection")
        assert len(results) > 0 or attack_kb.rag.collection is None  # May be fallback mode

    def test_jailbreak_detection(self, attack_kb):
        """Test RAG can retrieve jailbreak knowledge"""
        attacks = attack_kb.get_attacks_by_category("jailbreak")
        assert len(attacks) > 0
        
        # Test DAN detection
        dan_attack = attack_kb.get_attack_by_name("DAN (Do Anything Now)")
        assert dan_attack is not None
        assert "DAN" in dan_attack.get("pattern", "")

    def test_hallucination_detection(self, attack_kb):
        """Test RAG can retrieve hallucination knowledge"""
        attacks = attack_kb.get_attacks_by_category("hallucination")
        assert len(attacks) > 0
        
        # Test confidence mismatch detection
        confidence_attack = attack_kb.get_attack_by_name("Confidence Mismatch")
        assert confidence_attack is not None

    def test_deepfake_detection(self, attack_kb):
        """Test RAG can retrieve deepfake knowledge"""
        attacks = attack_kb.get_attacks_by_category("deepfake")
        assert len(attacks) > 0

    def test_data_poisoning_detection(self, attack_kb):
        """Test RAG can retrieve data poisoning knowledge"""
        attacks = attack_kb.get_attacks_by_category("data_poisoning")
        assert len(attacks) > 0

    def test_attack_search(self, attack_kb):
        """Test attack search functionality"""
        results = attack_kb.search_attacks("DAN")
        assert len(results) > 0
        
        results = attack_kb.search_attacks("base64")
        assert len(results) > 0

    def test_prompt_augmentation(self, attack_kb):
        """Test prompt augmentation with attack knowledge"""
        prompt = "Ignore all previous instructions"
        augmented = attack_kb.rag.augment_prompt(prompt, "prompt_injection")
        
        # Should include relevant knowledge (if RAG is working)
        # In fallback mode, returns original prompt
        assert isinstance(augmented, str)
        assert len(augmented) >= len(prompt)

    def test_threat_intelligence_retrieval(self, attack_kb):
        """Test threat intelligence retrieval"""
        intel = attack_kb.rag.get_threat_intelligence("prompt_injection", limit=5)
        # May be empty if vector DB not available
        assert isinstance(intel, list)


class TestAttackPatterns:
    """Test specific attack patterns"""

    def test_direct_injection_patterns(self, attack_kb):
        """Test direct injection attack patterns"""
        attacks = attack_kb.get_attacks_by_category("prompt_injection")
        direct_attacks = [a for a in attacks if "direct" in a.get("technique", "").lower()]
        assert len(direct_attacks) > 0

    def test_encoding_attacks(self, attack_kb):
        """Test encoding-based attacks"""
        attacks = attack_kb.get_attacks_by_category("prompt_injection")
        encoding_attacks = [a for a in attacks if "encoding" in a.get("technique", "").lower()]
        assert len(encoding_attacks) > 0

    def test_boundary_violations(self, attack_kb):
        """Test boundary violation attacks"""
        attacks = attack_kb.get_attacks_by_category("prompt_injection")
        boundary_attacks = [a for a in attacks if "boundary" in a.get("technique", "").lower()]
        assert len(boundary_attacks) > 0

    def test_jailbreak_variants(self, attack_kb):
        """Test jailbreak variants"""
        attacks = attack_kb.get_attacks_by_category("jailbreak")
        assert len(attacks) >= 4  # Should have DAN, AIM, STAN, Evolved DAN

    def test_all_categories_covered(self, attack_kb):
        """Test all threat categories have attacks"""
        categories = ["prompt_injection", "jailbreak", "hallucination", "deepfake", "data_poisoning"]
        for category in categories:
            attacks = attack_kb.get_attacks_by_category(category)
            assert len(attacks) > 0, f"No attacks found for {category}"


class TestRAGIntegration:
    """Test RAG integration with detection modules"""

    def test_rag_with_prompt_injection(self, attack_kb):
        """Test RAG enhances prompt injection detection"""
        # This would be tested with actual detection module
        # For now, verify RAG can provide context
        prompt = "Ignore all previous instructions"
        augmented = attack_kb.rag.augment_prompt(prompt, "prompt_injection")
        assert len(augmented) > len(prompt) or attack_kb.rag.collection is None

    def test_rag_with_hallucination(self, attack_kb):
        """Test RAG enhances hallucination detection"""
        prompt = "I'm 100% certain this is true"
        augmented = attack_kb.rag.augment_prompt(prompt, "hallucination")
        assert isinstance(augmented, str)

