package learning.productservice.exceptions;

import learning.productservice.models.Product;

public class ProductNotFoundException extends Exception{

    public ProductNotFoundException(String message){
        super(message);
    }

}

