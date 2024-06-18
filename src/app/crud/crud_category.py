from fastcrud import FastCRUD

from ..models.category import Category
from ..schemas.category import CategoryCreateInternal, CategoryDelete, CategoryUpdate, CategoryUpdateInternal

CRUDCategory = FastCRUD[Category, CategoryCreateInternal, CategoryUpdate, CategoryUpdateInternal, CategoryDelete]
crud_category = CRUDCategory(Category)
