from gallery import db


class Pond(db.Model):
    __tablename__ = 'ponds'
    id = db.Column(db.Integer, primary_key=True)
    name_id = db.Column(db.String(128), unique=True, nullable=False)
    uid = db.Column(db.String(128))
    promo_count = db.Column(db.Integer)
    todel_count = db.Column(db.Integer)
    overall_count = db.Column(db.Integer)
    last_offset = db.Column(db.Integer)
    pond_type = db.relationship('PondType', backref='ponds')
    type = db.Column(
        db.Integer, db.ForeignKey('pond_types.id'), nullable=False
    )
    pond_category = db.relationship('PondCategory', backref='ponds')
    category = db.Column(db.Integer, db.ForeignKey('pond_categories.id'))
    last_post = db.Column(db.String(255))
    fpath = db.Column(db.String(255))
    last_seen_at = db.Column(db.DateTime)


def get_pond_entry(pond_id: str) -> Pond:
    return Pond.query.filter_by(name_id=pond_id).first()


def filter_and_get_ponds(type_=None, category=None):
    if type_:
        type_entry = PondType.query.filter_by(name_id=type_).first()
        if type_entry:
            type_id = type_entry.id
            category_id = None
            if category:
                category_entry = PondCategory.query.filter_by(
                    name_id=category).first()
                if category_entry:
                    category_id = category_entry.id
        return Pond.query.filter_by(type=type_id, category=category_id).all()
    else:
        return Pond.query.all()


def update_pond_in_db(pond_id, data):
    overall_count = len(data['overall'])
    type_ = data['type']
    type_id = PondType.query.filter_by(name_id=type_).first().id
    check_and_update_types(type_)
    category_id = None
    category = data.get('category')
    if category:
        check_and_update_categories(category, type_)
        category_query = PondCategory.query.filter_by(name_id=category)
        category_id = category_query.first().id

    pond_entry = get_pond_entry(pond_id)
    if pond_entry:
        pond_entry.type = type_id
        pond_entry.category = category_id
        pond_entry.overall_count = overall_count
        promo_count = len(data['promo'])
        pond_entry.promo_count = promo_count
        todel_count = len(data['todel'])
        pond_entry.todel_count = todel_count
    else:
        pond_entry = Pond(
            name_id=pond_id,
            uid=pond_id,
            promo_count=0,
            todel_count=0,
            overall_count=overall_count,
            last_offset=0,
            type=type_id,
            category=category_id,
            fpath=data['fpath']
        )
        db.session.add(pond_entry)

    db.session.commit()


class PondType(db.Model):
    __tablename__ = 'pond_types'
    id = db.Column(db.Integer, primary_key=True)
    name_id = db.Column(db.String(128), unique=True, nullable=False)
    categories = db.relationship(
        'PondCategory', backref='pond_type', lazy=True
    )


def check_and_update_types(type_):
    if type_ not in get_all_types():
        new_type = PondType(name_id=type_)
        db.session.add(new_type)
        db.session.commit()


def get_all_types():
    result = PondType.query.all()
    return [x.name_id for x in result]


class PondCategory(db.Model):
    __tablename__ = 'pond_categories'
    id = db.Column(db.Integer, primary_key=True)
    name_id = db.Column(db.String(128), unique=True, nullable=False)
    pond_type_id = db.Column(
        db.Integer, db.ForeignKey('pond_types.id'), nullable=False
    )


def check_and_update_categories(category, type_):
    categories = get_categories_by_type(type_)
    if category not in categories:
        is_category_in_another_type = PondCategory.query.filter_by(
            name_id=category
        ).first()
        if not is_category_in_another_type:
            print(category)
            type_entry = PondType.query.filter_by(name_id=type_).first()
            new_category = PondCategory(
                name_id=category,
                pond_type_id=type_entry.id
            )
            db.session.add(new_category)
            db.session.commit()
        else:
            raise


def get_categories_by_type(name_id=None, id_=None):
    type_entry = None
    if name_id:
        type_entry = PondType.query.filter_by(name_id=name_id).first()
    elif id_:
        type_entry = PondType.query.filter_by(id=id_).first()
    result = PondCategory.query.filter_by(pond_type_id=type_entry.id).all()
    return [x.name_id for x in result]
