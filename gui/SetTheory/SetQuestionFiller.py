import random
import re
from sage.all import Set

class SetQuestionFiller:
    def __init__(self, universe=None, minSize=3, maxSize=6, forceValidPartition=False):
        if universe is None:
            universe = list(range(1, 11))
        self.universe = universe
        self.min_size = minSize
        self.max_size = maxSize
        self.force_valid_partition = forceValidPartition

    def randomSet(self):
        size = random.randint(self.min_size, self.max_size)
        return Set(random.sample(self.universe, size))

    def randomSubset(self, A, allow_empty=False):
        """Return a random subset of A. Default: non-empty subset."""
        elements = list(A)
        if not elements:
            return Set([])
        minSize = 0 if allow_empty else 1
        size = random.randint(minSize, len(elements))
        return Set(random.sample(elements, size))

    def randomPartition(self, A, k=3):
        elements = list(A)
        random.shuffle(elements)
        k = min(k, max(1, len(A)))
        groups = [[] for _ in range(k)]
        for elem in elements:
            groups[random.randint(0, k-1)].append(elem)

        # ensure nonempty groups
        for i in range(k):
            if not groups[i]:
                donors = [g for g in groups if len(g) > 1]
                if donors:
                    donor = random.choice(donors)
                    groups[i].append(donor.pop())
                else:
                    # all groups size 0 or 1, move from a random non-empty
                    nonempty = [g for g in groups if g]
                    if nonempty:
                        donor = random.choice(nonempty)
                        groups[i].append(donor.pop())
        return [Set(g) for g in groups]

    def fillTemplate(self, template):
        # placeholders like <setA>, <setB>, etc.
        labels = set(re.findall(r"<set([A-Z])>", template))
        substitutions = {}

        lower = template.lower()

        # 1) partition detection
        if "partition" in lower:
            # generate A first
            A = self.randomSet()
            substitutions["A"] = str(A)

            # create parts for the other labels
            otherLabels = sorted(labels - {"A"})
            if self.force_valid_partition:
                parts = self.randomPartition(A, k=len(otherLabels) if otherLabels else 1)
                # zip parts to labels (if fewer parts than labels, remaining labels get empty sets)
                for label, subset in zip(otherLabels, parts):
                    substitutions[label] = str(subset)
                for label in otherLabels[len(parts):]:
                    substitutions[label] = str(Set([]))
            else:
                # random subsets of A (may overlap / not cover A)
                for label in otherLabels:
                    substitutions[label] = str(self.randomSubset(A, allow_empty=False))

            # replace placeholders
            for label, s in substitutions.items():
                template = template.replace(f"<set{label}>", str(s))
            return template, substitutions

        # 2) subset-of-A detection: look for the subset symbol or the word 'subset'
        if "⊆" in template or "subset" in lower:
            # ensure we actually have A as a placeholder; if not, still generate A if needed
            A = self.randomSet()
            substitutions["A"] = A
            for label in sorted(labels):
                if label == "A":
                    continue
                substitutions[label] = str(self.randomSubset(A, allow_empty=False))
            # replace placeholders
            for label, s in substitutions.items():
                template = template.replace(f"<set{label}>", str(s))
            return template, substitutions

        # 3) normal case: independent random sets for each placeholder
        for label in labels:
            s = self.randomSet()
            substitutions[label] = str(s)
            template = template.replace(f"<set{label}>", str(s))

        return template, substitutions
