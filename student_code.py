import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment

    def kb_explain(self, fact_or_rule):
        """
        Explain where the fact or rule comes from

        Args:
            fact_or_rule (Fact or Rule) - Fact or rule to be explained

        Returns:
            string explaining hierarchical support from other Facts and rules
        """
        ####################################################
        # Student code goes here
        return_string = ""  # output string that will be returned in the end
        counter = 0  # keeps track of recursion. Will help in spacing
        if isinstance(fact_or_rule, Fact):  # checks if it is a fact
            fact = self._get_fact(fact_or_rule)
            if fact in self.facts:  # checks if fact is in kb
                return_string = "fact: " + fact.statement.__str__()
                if fact.asserted:  # checks if fact is asserted
                    return_string = return_string + " ASSERTED\n"
                else:
                    return_string += "\n"

                return_string += self.kb_supports(fact, counter)

            else:
                return_string = return_string + "Fact is not in the KB"

        elif isinstance(fact_or_rule, Rule):  # check if it is a rule
            rule = self._get_rule(fact_or_rule)
            if rule in self.rules:  # checks if a rule is in kb
                lhsstring = self.kb_print_rule(rule.lhs)  # converts left hand side to proper string format
                return_string = return_string + "rule: " + lhsstring + " -> " + rule.rhs  # concatenates return string

                if rule.asserted:
                    return_string = return_string + " ASSERTED\n"
                else:
                    return_string += "\n"

                return_string += self.kb_supports(rule, counter)

            else:
                return_string = return_string + "Rule is not in the KB"

        return return_string

    def kb_supports(self, f_or_r, counter):
        # counter += 1
        spaces = " "*counter*4;
        rs = ""
        if isinstance(f_or_r, Fact):
            fact = self._get_fact(f_or_r)
            if fact.supported_by:
                for sb in fact.supported_by:
                    rs = rs + spaces + "  SUPPORTED BY\n"
                    sup_fact = sb[0]
                    sup_rule = sb[1]

                    rs = rs + spaces + "    fact: " + sup_fact.statement.__str__()
                    if sup_fact.asserted is True:
                        rs = rs + " ASSERTED \n"
                    else:
                        rs += "\n"
                    new_counter = counter + 1
                    rs += self.kb_supports(sup_fact, new_counter)

                    lhsstring = self.kb_print_rule(sup_rule.lhs)
                    rs = rs + spaces + "    rule: " + lhsstring + " -> " + sup_rule.rhs.__str__()
                    if sup_rule.asserted is True:
                        rs = rs + " ASSERTED \n"
                    else:
                        rs += "\n"
                    new_counter = counter + 1
                    rs += self.kb_supports(sup_rule, new_counter)


        if isinstance(f_or_r, Rule):
            rule = self._get_rule(f_or_r)
            if rule.supported_by:

                for sb in rule.supported_by:
                    rs = rs + spaces + "  SUPPORTED BY \n"
                    sup_fact = sb[0]
                    sup_rule = sb[1]

                    rs = rs + spaces + "    fact: " + sup_fact.statement.__str__()
                    if sup_fact.asserted is True:
                        rs = rs + " ASSERTED \n"
                    else:
                        rs += "\n"
                    new_counter = counter + 1
                    rs += self.kb_supports(sup_fact, new_counter)

                    lhsstring = self.kb_print_rule(sup_rule.lhs)
                    rs = rs + spaces + "    rule: " + lhsstring + " -> " + sup_rule.rhs.__str__()
                    if sup_rule.asserted is True:
                        rs = rs + " ASSERTED \n"
                    else:
                        rs += "\n"
                    new_counter = counter + 1
                    rs += self.kb_supports(sup_rule, new_counter)

        return rs

    def kb_print_rule(self, rule_lhs):
        lhs_string = "("
        for i in rule_lhs:

            lhs_string += i.__str__() + ", "
        lhs_string = lhs_string.strip(", ")
        lhs_string += ")"

        return lhs_string



class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Implementation goes here
        # Not required for the extra credit assignment
