# uploads/tasks.py
from celery import shared_task
from .models import FileUpload, ActivityLog
import docx

@shared_task
def process_file_task(file_id):
    file_record = FileUpload.objects.get(id=file_id)
    try:
        file_path = file_record.file.path
        word_count = 0

        if file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                word_count = len(f.read().split())
        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            word_count = len(text.split())

        file_record.word_count = word_count
        file_record.status = "completed"
        file_record.save()

        ActivityLog.objects.create(
            user=file_record.user,
            action="File processed",
            metadata={"filename": file_record.filename, "word_count": word_count}
        )

    except Exception as e:
        file_record.status = "failed"
        file_record.save()

        ActivityLog.objects.create(
            user=file_record.user,
            action="Processing failed",
            metadata={"filename": file_record.filename, "error": str(e)}
        )
