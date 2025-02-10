from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

class BaseEmbedding(ABC):
    def __init__(self):
        # Load CLIP model
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def generate_embedding(self, input_data: Union[str, Image.Image]) -> List[float]:
        """
        Generate embedding for a single text or image.

        Args:
            input_data (Union[str, Image.Image]): Text or Image.

        Returns:
            List[float]: Embedding vector.
        """
        embeddings: List[List[float]] = self._call_embedding_model([input_data])
        return embeddings[0]

    def generate_batch_embeddings(self, inputs: List[Union[str, Image.Image]]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts or images.

        Args:
            inputs (List[Union[str, Image.Image]]): List of text or images.

        Returns:
            List[List[float]]: Embeddings for all inputs.
        """
        return self._call_embedding_model(inputs)

    @abstractmethod
    def _call_embedding_model(self, inputs: List[Union[str, Image.Image]]) -> List[List[float]]:
        pass

    def calculate_cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1 (List[float]): First embedding vector.
            embedding2 (List[float]): Second embedding vector.

        Returns:
            float: Cosine similarity score (-1 to 1).
        """
        vec1, vec2 = np.array(embedding1), np.array(embedding2)
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)


class CLIPEmbedding(BaseEmbedding):
    def _call_embedding_model(self, inputs: List[Union[str, Image.Image]]) -> List[List[float]]:
        """
        Calls the CLIP model for generating embeddings.

        Args:
            inputs (List[Union[str, Image.Image]]): List of text or images.

        Returns:
            List[List[float]]: Embeddings for each input.
        """
        # Check if input is text or image
        is_text = isinstance(inputs[0], str)
        is_image = isinstance(inputs[0], Image.Image)

        # Process input
        inputs_processed = self.processor(
            text=inputs if is_text else None,
            images=inputs if is_image else None,
            return_tensors="pt",
            padding=True
        )

        # Generate embeddings
        with torch.no_grad():
            outputs = self.model.get_text_features(**inputs_processed) if is_text else \
                      self.model.get_image_features(**inputs_processed)

        return outputs.cpu().numpy().tolist()
