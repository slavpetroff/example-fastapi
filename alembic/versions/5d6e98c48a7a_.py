"""empty message

Revision ID: 5d6e98c48a7a
Revises:
Create Date: 2025-01-09 13:32:53.983390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d6e98c48a7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_table('items',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('published', sa.Boolean(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('creator', sa.Integer(), nullable=True),
    sa.Column('image_url', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['creator'], ['users.id'], name='fk_items_users_id_creator', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_items_name', 'items', ['name'], unique=False)
    op.create_table('market',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('address', sa.String(length=100), nullable=True),
    sa.Column('city', sa.String(length=32), nullable=False),
    sa.Column('country', sa.String(length=32), nullable=True),
    sa.Column('owner', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['owner'], ['users.id'], name='fk_market_users_id_owner'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index('ix_market_city', 'market', ['city'], unique=False)
    op.create_index('ix_market_name', 'market', ['name'], unique=True)
    op.create_table('market_maintainers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('user', sa.Integer(), nullable=True),
    sa.Column('market', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['market'], ['market.id'], name='fk_market_maintainers_market_market_id', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user'], ['users.id'], name='fk_market_maintainers_users_user_id', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tags',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('item', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_tags_users_id_created_by', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['item'], ['items.id'], name='fk_tags_items_id_item', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index('ix_tags_name', 'tags', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_tags_name', table_name='tags')
    op.drop_table('tags')
    op.drop_table('market_maintainers')
    op.drop_index('ix_market_name', table_name='market')
    op.drop_index('ix_market_city', table_name='market')
    op.drop_table('market')
    op.drop_index('ix_items_name', table_name='items')
    op.drop_table('items')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
