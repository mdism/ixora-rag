import os
from django.db import models
from django.conf import settings
from pgvector.django import VectorField
from unstructured.documents.elements import Element
from api.models import Role


User = settings.AUTH_USER_MODEL

class Customer(models.Model):
    """
    Represents a company or customer.
    """
    name = models.CharField(max_length=255, unique=True)
    contact = models.EmailField(blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Represents categories for documents (e.g., Infra, Network, Cloud).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

def document_upload_to(instance, filename):
    customer_name = instance.customer.name.replace(" ", "_")
    tag_name = instance.tag.name.replace(" ", "_")
    return f"customers/{customer_name}/{tag_name}/{filename}"


class Document(models.Model):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, related_name="documents")
    tag = models.ForeignKey("Tag", on_delete=models.CASCADE, related_name="documents")
    file_name = models.CharField(max_length=255, blank=True)  # optional
    file = models.FileField(upload_to=document_upload_to)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="uploaded_documents")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.file_name and self.file:
            self.file_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file_name} ({self.customer.name} - {self.tag.name})"



class DocumentEmbedding(models.Model):
    document = models.ForeignKey("Document", on_delete=models.CASCADE, related_name="embeddings")
    chunk_text = models.TextField(blank=True, null=True)
    embedding = VectorField(dimensions=settings.EMBEDDING_MODEL_WEIGHT)

    # Metadata for Filtering (Crucial for multi-tenancy)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, null=True, blank=True)
    tag = models.ForeignKey("Tag", on_delete=models.DO_NOTHING, null=True, blank=True)
    
    # Metadata from Unstructured Elements (Crucial for RAG context/citations)
    page_number = models.IntegerField(null=True, blank=True)  # Page number for citation
    section_title = models.CharField(max_length=512, null=True, blank=True) # Section header for context
    
    # NEW: Parent Document Retrieval Support (Future-Proofing)
    # The parent_chunk_text will hold the larger, context-rich text 
    # while chunk_text holds the smaller text used for embedding.
    parent_chunk_text = models.TextField(null=True, blank=True) 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Embedding for {self.document.file_name} [Page {self.page_number}]"


# class DocumentEmbedding(models.Model):
#     document = models.ForeignKey("Document", on_delete=models.CASCADE, related_name="embeddings")
#     embedding = VectorField(dimensions=384)
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
#     tag = models.ForeignKey(Tag, on_delete=models.DO_NOTHING, null=True, blank=True)
#     chunk_text = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Embedding for {self.document.file_name} [{self.id}]"
    

# class LLMModels(models.Model):
#     MODEL_TYPE = (
#         ("open_source" , "Open Source"),
#         ('closed_source', ('Closed Source'))
#     )
#     name = models.CharField(max_length=50, blank=False, null=False)
#     model_weightname = models.CharField(max_length=100, blank=False, null=False)
#     model_type = models.CharField(max_length=20, choices=MODEL_TYPE, default='open_source')
#     isSelected = models.BooleanField(default=False)
#     path = models.CharField(blank=True, null=True)
#     api_key = models.CharField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name

# class LLMModels(models.Model):
#     MODEL_TYPE = (
#         ("open_source", "Open Source"),
#         ("closed_source", "Closed Source"),
#     )
#     PROVIDERS = (
#         ("llama", "LlamaCpp"),
#         ("openai", "OpenAI"),
#         ("gemini", "Google Gemini"),
#         ("anthropic", "Anthropic Claude"),
#     )

#     name = models.CharField(max_length=50)
#     model_weightname = models.CharField(max_length=100)
#     provider = models.CharField(max_length=50, choices=PROVIDERS, default="llama")
#     model_type = models.CharField(max_length=20, choices=MODEL_TYPE, default="open_source")

#     is_selected = models.BooleanField(default=False)
#     enabled = models.BooleanField(default=True)

#     path = models.CharField(max_length=200, blank=True, null=True)
#     api_key_ref = models.CharField(max_length=100, blank=True, null=True)  # e.g. "OPENAI_KEY_1", GEMINI_API_KEY_1

#     parameters = models.JSONField(default=dict, blank=True)  # flexible configs
#     description = models.TextField(blank=True, null=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.name} ({self.provider})"

class UserCustomerAssignment(models.Model):
    """
    Maps users to customer-specific tags.
    A user may have access to multiple tags within a customer.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_role_assignments")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="user_role_assignments")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_role_assignments")

    # class Meta:
    #     unique_together = ("user", "customer")

    def __str__(self):
        return f"{self.user} -> {self.customer} ({self.role})"


class ChatSession(models.Model):
    """
    Represents a chat session for a user.
    Note: The customer is tied to the *session* initially, but messages within it can be for different customers/providers.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    initial_customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="initial_chat_sessions")
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} by {self.user} (Init. Customer: {self.initial_customer})"


class ChatMessage(models.Model):
    """
    Stores messages exchanged in a chat session, including the provider and customer context for the query that generated it.
    """
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=50, choices=(("user", "User"), ("ai", "AI")))
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    provider = models.CharField(max_length=50, default="llama") # Default provider
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="chat_messages")

    def __str__(self):
        return f"{self.sender} ({self.provider}, {self.customer}): {self.message[:30]}..."

class QueryLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user_query = models.TextField()
    response = models.TextField()
    provider = models.CharField(max_length=50)
    context_snippet = models.TextField(blank=True, null=True)
    context_match_count = models.IntegerField(default=0)
    sources = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.timestamp} | {self.provider}"
    