from fastcrud import FastCRUD

from ..models.product import Product
from ..schemas.product import ProductCreateInternal, ProductDelete, ProductUpdate, ProductUpdateInternal

CRUDProduct = FastCRUD[Product, ProductCreateInternal, ProductUpdate, ProductUpdateInternal, ProductDelete]
crud_product = CRUDProduct(Product)
