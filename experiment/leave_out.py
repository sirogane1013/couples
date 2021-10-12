import git

from graph import Graph
from util.git import get_modified


def leave_one_out(commit: git.Commit, graph: Graph):
    """
    Parameters
    ----------
    commit: git.Commit
        Commit Object
    graph: Graph
        Coocc Graph

    Returns
    -------
    hexsha: str
        Commit Hash
    mrr: float
    recall: float
    feedback: float
    details: list[dict[str, int]]
        Detail of each trials
        format:
        {
            target: str -- target name of prediction
            rank: int   -- The rank target appeared
                           If prediction failed, it's value is -1.
        }

    Raises
    -------
    TooSmallCommitException
    """
    hexsha = commit.hexsha
    modified = get_modified(commit)
    if len(modified) <= 1:
        raise TooSmallCommitException("Commit size is too small to leave one out.")
    details = []
    f = 0
    for _ in range(len(modified)):
        modified.append(modified.pop(0))
        target = modified[0]
        query = modified[1:]
        answer = graph.guide(query)
        if len(answer) > 0:
            f += 1
        if target in answer:
            details.append({
                "target": target,
                "rank": answer.index(target) + 1
            })
        else:
            details.append({
                "target": target,
                "rank": -1
            })
    feedback = f / len(modified)
    mrr, recall = calc_metrics(details, feedback)
    return hexsha, mrr, recall, feedback, details


def calc_metrics(details, feedback):
    m = 0
    r = 0
    for detail in details:
        rank = detail["rank"]
        if rank > 0:
            r += 1
            m += 1 / rank
    mrr = m / (len(details) * feedback)
    recall = r / len(details)
    return mrr, recall


class TooSmallCommitException(Exception):
    pass
