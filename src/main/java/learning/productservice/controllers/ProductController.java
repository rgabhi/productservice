package learning.productservice.controllers;

import learning.productservice.dtos.FakeStoreProductDto;
import learning.productservice.exceptions.ProductNotFoundException;
import learning.productservice.models.Product;
import learning.productservice.services.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/products")
public class ProductController {
    ProductService productService;
    @Autowired
    ProductController(ProductService productService){
        this.productService = productService;
    }
   @GetMapping
    public ResponseEntity<List<Product>> getAllProducts(){
        return productService.getAllProducts();
    }
    @GetMapping("/{id}")
    public ResponseEntity<Product> getProductById(@PathVariable("id") long id) throws ProductNotFoundException {
        return productService.getSingleProduct(id);
    }

    @PostMapping()
    public ResponseEntity<Product> addNewProduct(@RequestBody FakeStoreProductDto fakeStoreProductDto){
        return productService.addProduct(fakeStoreProductDto);
    }

    @PatchMapping("/{id}")
    public ResponseEntity<Product> updateProduct(@PathVariable("id") Long id,@RequestBody FakeStoreProductDto fakeStoreProductDto){
       return productService.updateProduct(id,fakeStoreProductDto);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Product> replaceProduct(@PathVariable("id") Long id ,@RequestBody FakeStoreProductDto fakeStoreProductDto){
       return productService.replaceProduct(id, fakeStoreProductDto);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Product> deleteProduct(@PathVariable("id") Long id){
        return productService.deleteProduct(id);
    }

}
