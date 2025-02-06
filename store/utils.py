import pandas as pd
from books.models import Book, Author, Publisher, Genre, DEliveryOption
from cities_light.models import Country, Region, City
from store.models import Store

def process_csv(file, store):
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding='latin1')
    
    for _, row in df.iterrows():
        genre, _ = Genre.objects.get_or_create(name=row['genre'])
        publisher, _ = Publisher.objects.get_or_create(name=row['publisher'])
        book = Book.objects.create(
            title=row['title'],
            slug=row['slug'],
            quantity=row['quantity'],
            description=row['description'],
            number_of_pages=row['number_of_pages'],
            published_year=row['published_year'],
            language=row['language'],
            price=row['price'],
            genre=genre,
            publisher=publisher,
            store=store,
            status='pending'
        )
        authors = row['authors'].split(',')
        for author_name in authors:
            author, _ = Author.objects.get_or_create(name=author_name.strip())
            book.authors.add(author)
        
        # Process delivery options
        delivery_options = row['delivery_options'].split(';')
        for option in delivery_options:
            option_data = option.split(',')
            country = Country.objects.get(name=option_data[0].strip())
            region = Region.objects.get(name=option_data[1].strip(), country=country)
            city = City.objects.get(name=option_data[2].strip(), region=region)
            DEliveryOption.objects.create(
                book=book,
                delivery_option=option_data[3].strip(),
                country=country,
                region=region,
                city=city
            )
        
        book.save()