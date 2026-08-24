import pytest

from promptcore.domain.frameworks import FRAMEWORK_REGISTRY, TaskCategory
from promptcore.domain.frameworks.modern import (
    SelfDiscover,
    ChainOfDraft,
    Critic,
    ChainOfCode,
    Re2ReReading,
    ChainOfAbstraction,
    DeliberateThenGenerate,
)


class TestSelfDiscover:
    def test_registered(self):
        assert "self_discover" in FRAMEWORK_REGISTRY

    def test_metadata(self):
        info = SelfDiscover.get_info()
        assert info["name"] == "self_discover"
        assert TaskCategory.PLANNING in SelfDiscover.best_for
        assert SelfDiscover.complexity_threshold >= 6.0

    def test_template_mentions_task(self):
        fw = SelfDiscover()
        template = fw.generate_prompt_template("Design a caching strategy")
        assert "Design a caching strategy" in template
        assert len(template) > 200


class TestChainOfDraft:
    def test_registered(self):
        assert "chain_of_draft" in FRAMEWORK_REGISTRY

    def test_metadata(self):
        info = ChainOfDraft.get_info()
        assert info["name"] == "chain_of_draft"
        assert TaskCategory.MATH in ChainOfDraft.best_for
        assert ChainOfDraft.complexity_threshold <= 4.0

    def test_template_mentions_task(self):
        fw = ChainOfDraft()
        template = fw.generate_prompt_template("Compute the average of these readings")
        assert "Compute the average of these readings" in template
        assert "five words" in template


class TestCritic:
    def test_registered(self):
        assert "critic" in FRAMEWORK_REGISTRY

    def test_metadata(self):
        info = Critic.get_info()
        assert info["name"] == "critic"
        assert TaskCategory.RESEARCH in Critic.best_for
        assert Critic.complexity_threshold >= 5.0

    def test_template_mentions_task(self):
        fw = Critic()
        template = fw.generate_prompt_template("Evaluate the credibility of this source")
        assert "Evaluate the credibility of this source" in template
        assert len(template) > 200


class TestChainOfCode:
    def test_registered(self):
        assert "chain_of_code" in FRAMEWORK_REGISTRY

    def test_metadata(self):
        info = ChainOfCode.get_info()
        assert info["name"] == "chain_of_code"
        assert TaskCategory.CODE in ChainOfCode.best_for
        assert ChainOfCode.complexity_threshold >= 5.0

    def test_template_mentions_task(self):
        fw = ChainOfCode()
        template = fw.generate_prompt_template("Compute checksums over large log files")
        assert "Compute checksums over large log files" in template
        assert "emulat" in template.lower()


class TestRe2ReReading:
    def test_registered(self):
        assert "re2_re_reading" in FRAMEWORK_REGISTRY

    def test_metadata(self):
        info = Re2ReReading.get_info()
        assert info["name"] == "re2_re_reading"
        assert TaskCategory.MATH in Re2ReReading.best_for
        assert Re2ReReading.complexity_threshold <= 3.0

    def test_template_mentions_task_twice(self):
        fw = Re2ReReading()
        task = "What is 17% of 240?"
        template = fw.generate_prompt_template(task)
        assert template.count(task) == 2
        assert len(template) > 200


class TestChainOfAbstraction:
    def test_registered(self):
        assert "chain_of_abstraction" in FRAMEWORK_REGISTRY

    def test_metadata(self):
        info = ChainOfAbstraction.get_info()
        assert info["name"] == "chain_of_abstraction"
        assert TaskCategory.DATA in ChainOfAbstraction.best_for
        assert ChainOfAbstraction.complexity_threshold >= 4.0

    def test_template_mentions_task(self):
        fw = ChainOfAbstraction()
        template = fw.generate_prompt_template("Model the revenue flow between these entities")
        assert "Model the revenue flow between these entities" in template
        assert "placeholder" in template.lower()


class TestDeliberateThenGenerate:
    def test_registered(self):
        assert "deliberate_then_generate" in FRAMEWORK_REGISTRY

    def test_metadata(self):
        info = DeliberateThenGenerate.get_info()
        assert info["name"] == "deliberate_then_generate"
        assert TaskCategory.CREATIVE in DeliberateThenGenerate.best_for
        assert DeliberateThenGenerate.complexity_threshold >= 3.0

    def test_template_mentions_task(self):
        fw = DeliberateThenGenerate()
        template = fw.generate_prompt_template("Write a product announcement")
        assert "Write a product announcement" in template
        assert len(template) > 200
