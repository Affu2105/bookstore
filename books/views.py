from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import uuid
from books.s3_utils import upload_file_to_s3, delete_file_from_s3

def home(request):
    return render(request, 'home.html')

def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})

def add_book(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        price = request.POST.get("price")
        category = request.POST.get("category")
        description = request.POST.get('description')
        image = request.FILES.get("image")
        
        image_url = None
        if image:
            if settings.USE_S3:
                # Generate a unique filename to avoid collisions
                file_extension = os.path.splitext(image.name)[1]
                unique_filename = f"book_images/{uuid.uuid4()}{file_extension}"
                
                # Upload to S3
                image_url = upload_file_to_s3(image, unique_filename)
                
                # Only save the image filename in the database if upload was successful
                if image_url:
                    book = Book.objects.create(
                        title=title,
                        author=author,
                        price=price,
                        category=category,
                        description=description,
                        image_url=image_url,  # Store the S3 URL
                        s3_key=unique_filename  # Store the S3 key for deletion later
                    )
                else:
                    # Handle failed upload
                    book = Book.objects.create(
                        title=title,
                        author=author,
                        price=price,
                        category=category,
                        description=description
                    )
            else:
                # Use local file storage if S3 is not enabled
                fs = FileSystemStorage()
                image_name = fs.save(image.name, image)
                image_url = fs.url(image_name)
                
                book = Book.objects.create(
                    title=title,
                    author=author,
                    price=price,
                    category=category,
                    description=description,
                    image=image
                )
        else:
            # No image provided
            book = Book.objects.create(
                title=title,
                author=author,
                price=price,
                category=category,
                description=description
            )
            
        return redirect("book_list")

    return render(request, "add_book.html")

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'book_detail.html', {'book': book})

def update_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == "POST":
        book.title = request.POST.get("title")
        book.author = request.POST.get("author")
        book.category = request.POST.get("category")
        book.price = request.POST.get("price")
        book.description = request.POST.get("description")

        # Handle image upload
        if request.FILES.get("image"):
            image = request.FILES["image"]
            
            # Delete old image from S3 if it exists
            if settings.USE_S3 and book.s3_key:
                delete_file_from_s3(book.s3_key)
                
                # Upload new image to S3
                file_extension = os.path.splitext(image.name)[1]
                unique_filename = f"book_images/{uuid.uuid4()}{file_extension}"
                image_url = upload_file_to_s3(image, unique_filename)
                
                if image_url:
                    book.image_url = image_url
                    book.s3_key = unique_filename
            else:
                # Use local storage
                if book.image:
                    # Delete old image
                    if os.path.isfile(book.image.path):
                        os.remove(book.image.path)
                
                book.image = image

        book.save()
        return redirect("book_detail", book_id=book.id)

    return render(request, "update_book.html", {"book": book})

def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == "POST":
        # Delete image from S3 if it exists
        if settings.USE_S3 and book.s3_key:
            delete_file_from_s3(book.s3_key)
        elif book.image:
            # Delete local image file
            if os.path.isfile(book.image.path):
                os.remove(book.image.path)
                
        book.delete()
        return redirect("book_list")  # Redirect to book list after deletion
        
    return render(request, "confirm_delete.html", {"book": book})