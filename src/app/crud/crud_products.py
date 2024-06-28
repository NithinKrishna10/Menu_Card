from fastcrud import FastCRUD

from ..models.product import Product , ProductPortion
from ..schemas.product import ProductCreateInternal, ProductDelete, ProductUpdate, ProductUpdateInternal , ProductPortionCreate,ProductPortionUpdate

CRUDProduct = FastCRUD[Product, ProductCreateInternal, ProductUpdate, ProductUpdateInternal, ProductDelete]
crud_product = CRUDProduct(Product)

CRUDProductPortion = FastCRUD[ProductPortion, ProductPortionCreate, ProductPortionUpdate, None, None]
crud_product_portion = CRUDProductPortion(ProductPortion)
