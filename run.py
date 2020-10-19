from listo_backend_moduals import app


if __name__ == "__main__":

    app.run(debug=True)

    """db.drop_all()
    db.create_all()
    
    from listo_backend_moduals.models import *
    u = User(id=1, email="em", password="123", username="K")
    print(u)
    print(u.posts)
    u.posts.append(Post(id =5, content="test", address_id=112))
    print(u.posts)
    m1 = Map_Address(id=112, latitude=0.5, lontitude=0.4)
    m2 = Map_Address(id=113, latitude=0.6, lontitude=0.4)
    u.been_to_ID_list.append(m1)
    u.been_to_ID_list.append(m2)
    print("enter successfully")
    db.session.add_all([u, m1, m2])
    db.session.commit()"""
