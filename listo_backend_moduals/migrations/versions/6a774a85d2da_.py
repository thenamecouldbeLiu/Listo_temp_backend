"""empty message

Revision ID: 6a774a85d2da
Revises: 
Create Date: 2020-12-08 00:49:21.850120

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6a774a85d2da'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tag')
    op.drop_table('placeList')
    op.drop_table('place')
    op.drop_table('user')
    op.drop_table('Mark')
    op.drop_table('tagRelationship')
    op.drop_table('place_relations')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('place_relations',
    sa.Column('place_rt', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('placelist_rt', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['place_rt'], ['place.id'], name='place_relations_place_rt_fkey'),
    sa.ForeignKeyConstraint(['placelist_rt'], ['placeList.id'], name='place_relations_placelist_rt_fkey')
    )
    op.create_table('tagRelationship',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('tag_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('place_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('user_id', 'tag_id', 'place_id', name='tagRelationship_pkey')
    )
    op.create_table('Mark',
    sa.Column('gmap_id', sa.INTEGER(), server_default=sa.text('nextval(\'"Mark_gmap_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('latitude', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('longitude', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('gmap_id', name='Mark_pkey')
    )
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('user_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('username', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('is_deleted', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('created_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('privacy', postgresql.ENUM('Auth_user', 'Normal_user', 'Deleted', name='authority'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('email', name='user_email_key'),
    sa.UniqueConstraint('username', name='user_username_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('place',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('latitude', sa.NUMERIC(precision=8, scale=0), autoincrement=False, nullable=False),
    sa.Column('longitude', sa.NUMERIC(precision=8, scale=0), autoincrement=False, nullable=False),
    sa.Column('phone', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('address', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('gmap_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('type', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('system_tag', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='place_pkey'),
    sa.UniqueConstraint('address', name='place_address_key'),
    sa.UniqueConstraint('gmap_id', name='place_gmap_id_key'),
    sa.UniqueConstraint('name', name='place_name_key'),
    sa.UniqueConstraint('phone', name='place_phone_key')
    )
    op.create_table('placeList',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"placeList_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=1000), autoincrement=False, nullable=False),
    sa.Column('privacy', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('coverImageURL', sa.VARCHAR(length=300), autoincrement=False, nullable=True),
    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='placeList_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='placeList_pkey')
    )
    op.create_table('tag',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=300), autoincrement=False, nullable=False),
    sa.Column('type', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='tag_pkey')
    )
    # ### end Alembic commands ###
