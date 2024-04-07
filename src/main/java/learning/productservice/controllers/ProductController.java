package learning.productservice.controllers;

import learning.productservice.commons.AuthenticationCommons;
import learning.productservice.dtos.ExceptionDto;
import learning.productservice.dtos.FakeStoreProductDto;
import learning.productservice.dtos.Role;
import learning.productservice.dtos.UserDto;
import learning.productservice.exceptions.ProductNotCreatedException;
import learning.productservice.exceptions.ProductNotFoundException;
import learning.productservice.models.Category;
import learning.productservice.models.Product;
import learning.productservice.services.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/products")
public class ProductController {
    private ProductService productService;
    private AuthenticationCommons authenticationCommons;
    //fakeProductService - use for caching example
    @Autowired
    ProductController(@Qualifier("selfProductService") ProductService productService,
                      RestTemplate restTemplate,
                      AuthenticationCommons authenticationCommons){
        this.productService = productService;
        this.authenticationCommons = authenticationCommons;

    }
   @GetMapping()
    public ResponseEntity<List<Product>> getAllProducts() throws ProductNotFoundException{
//       UserDto userDto = authenticationCommons.validateToken(token);
//       if(userDto== null) {
//            return new ResponseEntity<>(HttpStatus.FORBIDDEN);
//       }
//       boolean isAdmin = false;
//       for(Role role : userDto.getRoles()){
//           if(role.getName().equals("ADMIN")){
//               isAdmin = true;
//               break;
//           }
//       }
//
//       if(!isAdmin)return new ResponseEntity<>(HttpStatus.UNAUTHORIZED);

       return new ResponseEntity<>(productService.getAllProducts(), HttpStatus.OK);

    }
    @GetMapping("/{id}")
    public ResponseEntity<Product> getProductById(@PathVariable("id") long id) throws ProductNotFoundException {
        return new ResponseEntity<>(productService.getSingleProduct(id), HttpStatus.OK);
    }

    @PostMapping()
    public ResponseEntity<Product> addNewProduct(@RequestBody FakeStoreProductDto fakeStoreProductDto) throws ProductNotCreatedException {
        Product product= new Product();
        Category category = new Category();
        category.setName(fakeStoreProductDto.getCategory());
        product.setTitle(fakeStoreProductDto.getTitle());
        product.setDescription(fakeStoreProductDto.getDescription());
        product.setImageUrl(fakeStoreProductDto.getImage());
        product.setCategory(category);
        product.setPrice(fakeStoreProductDto.getPrice());
        return new ResponseEntity<>(productService.addProduct(product), HttpStatus.OK);
    }

    @PatchMapping("/{id}")
    public ResponseEntity<Product> updateProduct(@PathVariable("id") Long id,@RequestBody FakeStoreProductDto fakeStoreProductDto) throws ProductNotFoundException {
        Product product = new Product();
        product.setTitle(fakeStoreProductDto.getTitle());
        product.setDescription(fakeStoreProductDto.getDescription());
        product.setPrice(fakeStoreProductDto.getPrice());
        product.setImageUrl(fakeStoreProductDto.getImage());
        if(fakeStoreProductDto.getCategory() != null){
            Category category= new Category();
            category.setName(fakeStoreProductDto.getCategory());
            product.setCategory(category);
        }
       return new ResponseEntity<>(productService.updateProduct(id,product), HttpStatus.OK);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Product> replaceProduct(@PathVariable("id") Long id ,@RequestBody FakeStoreProductDto fakeStoreProductDto) throws ProductNotFoundException {
        Product product= new Product();
        Category category = new Category();
        category.setName(fakeStoreProductDto.getCategory());
        product.setTitle(fakeStoreProductDto.getTitle());
        product.setDescription(fakeStoreProductDto.getDescription());
        product.setImageUrl(fakeStoreProductDto.getImage());
        product.setCategory(category);
        product.setPrice(fakeStoreProductDto.getPrice());
        return new ResponseEntity<>(productService.replaceProduct(id, product), HttpStatus.OK);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable("id") Long id){
        productService.deleteProduct(id);
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @ExceptionHandler(ProductNotCreatedException.class)
    public ResponseEntity<ExceptionDto> handleProductNotCreatedException(ProductNotCreatedException e){
        ExceptionDto exceptionDto = new ExceptionDto();
        exceptionDto.setMessage(e.getMessage());
        exceptionDto.setDetail("Please check you if you provided the response object correctly.");
        return new ResponseEntity<>(exceptionDto, HttpStatus.BAD_REQUEST);
    }

}
