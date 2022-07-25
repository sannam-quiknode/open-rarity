import numpy as np
from openrarity.models.collection import Collection
from openrarity.models.token import Token
from openrarity.models.token_metadata import StringAttributeValue
from openrarity.scoring.base import BaseRarityFormula
from openrarity.scoring.utils import get_attr_probs_weights
import scipy


class InformationContentRarity(BaseRarityFormula):
    """This formula computes rarity of each token
    based on the idea of entropy and information content"""

    def score_token(self, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""

        # Scores are already inverted probabilities ,
        # We need to take sum of logarithms to estimate
        # information content.
        scores, _ = get_attr_probs_weights(token, normalized)

        collection_probabilities = self.get_collection_probabilities(
            collection=token.collection
        )
        # Scores are already inverted probabilities ,
        # We need to take sum of logarithms to estimate
        # information content.
        information_content = sum(np.log2(scores))
        collection_entropy = scipy.stats.entropy(collection_probabilities)

        return information_content / collection_entropy

    def get_collection_probabilities(self, collection: Collection):
        collection_attributes: dict[
            str, list[StringAttributeValue]
        ] = collection.extract_collection_attributes
        collection_null_attributes: dict[
            str, StringAttributeValue
        ] = collection.extract_null_attributes

        # collect all probabilities into array
        collection_probabilities = []
        for value, _ in collection_attributes.items():
            collection_attributes[value].append(
                collection_null_attributes[value]
            )

            collection_probabilities.extend(
                [
                    value.count / collection.token_total_supply
                    for value in collection_attributes[value]
                ]
            )