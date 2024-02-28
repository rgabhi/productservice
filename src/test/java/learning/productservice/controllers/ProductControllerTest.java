package learning.productservice.controllers;

import learning.productservice.exceptions.ProductNotFoundException;
import learning.productservice.models.Product;
import learning.productservice.services.ProductService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.ResponseEntity;

import java.util.ArrayList;
import java.util.List;
import java.util.PropertyPermission;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

@SpringBootTest
class ProductControllerTest {

    @Autowired
    private ProductController productController;

    @MockBean
    private ProductService productService;
    @Test
    void testProductSameAsService() throws ProductNotFoundException {

        // arrange
        List<Product> productList = new ArrayList<>();
        Product p1 = new Product();
        p1.setTitle("Iphone 15");
        Product p2 = new Product();
        p2.setTitle("Galaxy Z-Flip5");
        Product p3 = new Product();
        p3.setTitle("Samsung - ring");
        productList.add(p1);
        productList.add(p2);
        productList.add(p3);

        // pass a list copy for mocking since it can be mutated,
        // otherwise it will wrongly pass the test case.
        List<Product> productsToPass = new ArrayList<>();
        for(Product p : productList){
            Product pTemp = new Product();
            pTemp.setTitle(p.getTitle());
            productsToPass.add(pTemp);
        }
        when(
                productService.getAllProducts()
        ).thenReturn(
                productsToPass
        );

        //act
        ResponseEntity<List<Product>> response =  productController.getAllProducts();
        List<Product> productsInResponse = response.getBody();
        //assert
        assertEquals(productList.size(), productsInResponse.size());
        for(int i = 0;  i < productsInResponse.size(); i++){
            assertEquals(productList.get(i).getTitle(), productsInResponse.get(i).getTitle());
        }
    }
}