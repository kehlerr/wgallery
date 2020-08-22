from wgallery import db


class Catalog(db.Model):
    __tablename__ = 'catalogs'
    id = db.Column(db.Integer, primary_key=True)
    name_id = db.Column(db.String(128), unique=True, nullable=False)
    uid = db.Column(db.String(128))
    promo_count = db.Column(db.Integer)
    todel_count = db.Column(db.Integer)
    overall_count = db.Column(db.Integer)
    last_offset = db.Column(db.Integer)
    catalog_type = db.relationship('CatalogType', backref='catalogs')
    type = db.Column(
        db.Integer, db.ForeignKey('catalog_types.id'), nullable=False
    )
    catalog_category = db.relationship('CatalogCategory', backref='catalogs')
    category = db.Column(db.Integer, db.ForeignKey('catalog_categories.id'))
    last_post = db.Column(db.String(255))
    fpath = db.Column(db.String(255))
    last_seen_at = db.Column(db.DateTime)


def get_catalog_entry(catalog_id: str) -> Catalog:
    return Catalog.query.filter_by(name_id=catalog_id).first()


def filter_and_get_catalogs(type_=None, category=None):
    if not type_:
        return Catalog.query.all()

    type_entry = CatalogType.query.filter_by(name_id=type_).first()
    if type_entry:
        type_id = type_entry.id
        category_id = None
        if category:
            category_entry = CatalogCategory.query.filter_by(
                name_id=category).first()
            if category_entry:
                category_id = category_entry.id
    return Catalog.query.filter_by(type=type_id, category=category_id).all()


def update_catalog_in_db(catalog_id, data):
    overall_count = len(data['overall'])
    type_ = data['type']
    check_and_update_types(type_)
    type_id = CatalogType.query.filter_by(name_id=type_).first().id
    category_id = None
    category = data.get('category')
    if category:
        check_and_update_categories(category, type_)
        category_query = CatalogCategory.query.filter_by(name_id=category)
        category_id = category_query.first().id

    catalog_entry = get_catalog_entry(catalog_id)
    if catalog_entry:
        catalog_entry.type = type_id
        catalog_entry.category = category_id
        catalog_entry.overall_count = overall_count
        promo_count = len(data['promo'])
        catalog_entry.promo_count = promo_count
        todel_count = len(data['todel'])
        catalog_entry.todel_count = todel_count
    else:
        catalog_entry = Catalog(
            name_id=catalog_id,
            uid=catalog_id,
            promo_count=0,
            todel_count=0,
            overall_count=overall_count,
            last_offset=0,
            type=type_id,
            category=category_id,
            fpath=data['fpath']
        )
        db.session.add(catalog_entry)

    db.session.commit()


class CatalogType(db.Model):
    __tablename__ = 'catalog_types'
    id = db.Column(db.Integer, primary_key=True)
    name_id = db.Column(db.String(128), unique=True, nullable=False)
    categories = db.relationship(
        'CatalogCategory', backref='catalog_type', lazy=True
    )


def check_and_update_types(type_):
    if type_ not in get_all_types():
        new_type = CatalogType(name_id=type_)
        db.session.add(new_type)
        db.session.commit()


def get_all_types():
    result = CatalogType.query.all()
    return [x.name_id for x in result]


class CatalogCategory(db.Model):
    __tablename__ = 'catalog_categories'
    id = db.Column(db.Integer, primary_key=True)
    name_id = db.Column(db.String(128), unique=True, nullable=False)
    catalog_type_id = db.Column(
        db.Integer, db.ForeignKey('catalog_types.id'), nullable=False
    )


def check_and_update_categories(category, type_):
    categories = get_categories_by_type(type_)
    if category not in categories:
        is_category_in_another_type = CatalogCategory.query.filter_by(
            name_id=category
        ).first()
        if not is_category_in_another_type:
            print(category)
            type_entry = CatalogType.query.filter_by(name_id=type_).first()
            new_category = CatalogCategory(
                name_id=category,
                catalog_type_id=type_entry.id
            )
            db.session.add(new_category)
            db.session.commit()
        else:
            raise


def get_categories_by_type(name_id=None, id_=None):
    type_entry = None
    if name_id:
        type_entry = CatalogType.query.filter_by(name_id=name_id).first()
    elif id_:
        type_entry = CatalogType.query.filter_by(id=id_).first()
    type_id = type_entry.id
    result = CatalogCategory.query.filter_by(catalog_type_id=type_id).all()
    return [x.name_id for x in result]
