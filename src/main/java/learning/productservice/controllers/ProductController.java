package learning.productservice.controllers;

import learning.productservice.dtos.FakeStoreProductDto;
import learning.productservice.models.Product;
import learning.productservice.services.FakeProductService;
import learning.productservice.services.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
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
    public List<Product> getAllProducts(){
        return new ArrayList<>();
    }
    @GetMapping("/{id}")
    public Product getProductById(@PathVariable("id") long id){
       return productService.getSingleProduct(id);
    }

    @PostMapping()
    public Product addNewProduct(@RequestBody FakeStoreProductDto fakeStoreProductDto){
        return productService.addSingleProduct(fakeStoreProductDto);
    }

    @PatchMapping("/{id}")
    public Product updateProduct(@PathVariable("id") Long id,@RequestBody Product product){
       return new Product();
    }

    @PutMapping("/{id}")
    public Product replaceProduct(@PathVariable("id") Long id ,@RequestBody Product product){
       return new Product();
    }

    @DeleteMapping("/{id}")
    public void deleteProduct(@PathVariable("id") Long id){

    }


}
