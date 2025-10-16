from django.contrib import admin

from .models import Customer, Tag, Document, ChatSession, ChatMessage, DocumentEmbedding,UserCustomerAssignment, QueryLog
# Register your models here.


admin.site.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display=('__all__')
    search_fields = ('name')
    list_filter = ("created_at")

admin.site.register(QueryLog)
class CustomerQueryLog(admin.ModelAdmin):
    list_display=('__all__')
    # search_fields = ('name')
    # list_filter = ("created_at")


admin.site.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display=('__all__')
    search_fields = ('name')
    list_filter = ("created_at")

admin.site.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('__all__')
#     search_list = ('name')
#     list_filter = ('created_at')

admin.site.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display=('__all__')
#     search_fields = ('name')
#     list_filter = ('created_at')

admin.site.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display= ('__all__')
#     search_fields = ('name')
#     list_filter = ('created_at')

admin.site.register(DocumentEmbedding)
class DocumentEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('__all__')
#     search_fields = ('name')
#     list_filter=('created_at')

admin.site.register(UserCustomerAssignment)
class UserCustomerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('__all__')
#     # search_fields = ('name')
#     list_filter=('created_at')

