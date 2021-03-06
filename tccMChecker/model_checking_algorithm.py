"""This module implements the algorithm for LTL model checking."""

from __future__ import print_function

from tarjan import tarjan

from closure import get_closure
from model_checking_graph import get_all_atoms, get_model_checking_atoms, \
    get_model_checking__graph
from searching_algorithm import get_model_checking_scc_subgraphs, get_initial_nodes, \
    is_self_fulfilling, initial_nodes_entail_formula


def model_satisfies_property(formula, tcc_structure):
    """
    Checks if a model satisfies a formula.

    :param formula: Formula
    :type formula: :py:class:`~formula.Formula`

    :param tcc_structure: tcc Structure
    :type tcc_structure: Dictionary

    :returns: ``True`` if the model satisfies the formula or ``False`` otherwise.
    :rtype: Boolean

    :Example:

    >>> from tccMChecker.model_checking_algorithm import *
    >>> tcc_structure = {
    ... 1: {"store": [Formula({"":"in=true"})], "normal": [], "temporal": ["t4","p9"], "edges": [2,3], "initial": True},
    ... 2: {"store": [Formula({"": "x=2"}),Formula({"": "in=true"})], "normal": [], "temporal": ["t4","p9"], "edges": [2,3], "initial": False},
    ... 3: {"store": [Formula({"": "x=2"}),Formula({"~": "in=true"})], "normal": ["now2"], "temporal": ["t7","p9"], "edges": [5,6], "initial": False},
    ... 4: {"store": [Formula({"~": "in=true"})], "normal": ["now2"], "temporal": ["t7","p9"], "edges": [5,6], "initial": True},
    ... 5: {"store": [Formula({"": "x=1"}),Formula({"": "in=true"})], "normal": [], "temporal": ["t4","p9"], "edges": [2,3], "initial": False},
    ... 6: {"store": [Formula({"": "x=1"}),Formula({"~": "in=true"})], "normal": ["now2"], "temporal": ["t7","p9"], "edges": [5,6], "initial": False}
    ... }
    >>> formula = Formula({"<>": {"^":{"":"in=true","~":{"o":"x=2"}}}})
    >>> model_satisfies_property(formula, tcc_structure)
    False

    .. note:: The model checking algorithm is based on the work performed by
        Falaschi and Villanueva [FV06]_. For this reason, we need to use the
        negation of the formula as input of this function and we say that the
        model satisfies the property if this function returns ``False`` (i.e the
        model does not satisfy the negation of the formula).

    .. seealso::
        :py:class:`formula.Formula`
        
    """

    # Closure
    closure = []
    get_closure(formula, closure)

    print("Closure: {} formulas".format(len(closure)))
    for formula_closure in closure:
        print(formula_closure.get_formula())

    # All possible atoms
    atoms = get_all_atoms(closure)

    # Model Checking Atoms
    model_checking_atoms = get_model_checking_atoms(tcc_structure, atoms)

    for tcc_node in model_checking_atoms.keys():
        tcc_atoms = model_checking_atoms.get(tcc_node)
        print("Atom State {} ({})".format(tcc_node, len(tcc_atoms)))

        for atom_index in tcc_atoms.keys():
            print("Atom ", atom_index)

            for formula_atom in tcc_atoms.get(atom_index):
                print(formula_atom.get_formula(), " | ", )

            print("\n")

    # Model Checking Graph
    model_checking_graph = get_model_checking__graph(tcc_structure,
                                                     model_checking_atoms)
    print("Model Checking Graph: {} nodes".format(
        max(model_checking_graph.keys())))
    print(model_checking_graph)

    # Strongly Connected Components
    strongly_connected_components = tarjan(model_checking_graph)
    print("Strongly Connected Components: ")
    print(strongly_connected_components)

    model_checking_scc_subgraphs = get_model_checking_scc_subgraphs(
        strongly_connected_components, tcc_structure, model_checking_atoms,
        model_checking_graph)
    print("Model Checking SCC Subgraphs:", len(model_checking_scc_subgraphs))
    print(model_checking_scc_subgraphs)

    # Self-Fulfilling SCC and Initial Nodes
    initial_nodes = get_initial_nodes(tcc_structure, model_checking_atoms)
    for scc_n, scc_graph in enumerate(model_checking_scc_subgraphs):
        self_fulfilling_scc = is_self_fulfilling(scc_graph, initial_nodes,
                                                 model_checking_atoms)
        entail_formula = initial_nodes_entail_formula(scc_graph, initial_nodes,
                                                      model_checking_atoms,
                                                      formula)

        print("SCC Graph", scc_n, ":")
        print("is Self Fulfilling: ", self_fulfilling_scc)
        print("Initial Nodes Entail Formula: ", entail_formula)

        if self_fulfilling_scc and entail_formula:
            return True

    return False

