package learning.productservice.services;

import learning.productservice.dtos.FakeStoreProductDto;
import learning.productservice.exceptions.ProductNotCreatedException;
import learning.productservice.exceptions.ProductNotFoundException;
import learning.productservice.models.Category;
import learning.productservice.models.Product;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

@Service
public class FakeProductService implements ProductService {

    private RestTemplate restTemplate;
    @Autowired
    FakeProductService(RestTemplate restTemplate){
        this.restTemplate = restTemplate;
    }

    private Product convertFakeStoreProductToProduct(FakeStoreProductDto fakeStoreProductDto){
        Product product = new Product();
        product.setId(fakeStoreProductDto.getId());
        product.setTitle(fakeStoreProductDto.getTitle());
        product.setPrice(fakeStoreProductDto.getPrice());
        product.setDescription(fakeStoreProductDto.getDescription());
        product.setImageUrl(fakeStoreProductDto.getImage());
        product.setCategory(new Category());
        product.getCategory().setName(fakeStoreProductDto.getCategory());
        return product;

    }
    @Override
    public ResponseEntity<Product> getSingleProduct(Long id) throws ProductNotFoundException {
        FakeStoreProductDto productDto = restTemplate.getForObject("https://fakestoreapi.com/products/" + id, FakeStoreProductDto.class);
        if(productDto == null){
            throw new ProductNotFoundException("Product with id: "+ id + " not found!");
        }
        return new ResponseEntity<>(convertFakeStoreProductToProduct(productDto),HttpStatus.OK);
    }

    @Override
    public ResponseEntity<List<Product>> getAllProducts() throws ProductNotFoundException {
        FakeStoreProductDto[] productDto = restTemplate.getForObject("https://fakestoreapi.com/products/", FakeStoreProductDto[].class);
        List<Product> productList = new ArrayList<>();
        if(productDto == null){
            throw  new ProductNotFoundException("No products to show :(");
        }
        for(FakeStoreProductDto fakeProductDto : productDto){
            productList.add(convertFakeStoreProductToProduct(fakeProductDto));
        }
        return new ResponseEntity<>(productList, HttpStatus.OK);
    }

    @Override
    public  ResponseEntity<Product> addProduct(FakeStoreProductDto fakeStoreProductDto) throws ProductNotCreatedException {
        HttpEntity<FakeStoreProductDto> request = new HttpEntity<>(fakeStoreProductDto);
        FakeStoreProductDto productDto = restTemplate.postForObject("https://fakestoreapi.com/products", request, FakeStoreProductDto.class);
        if(productDto == null){
            throw new ProductNotCreatedException("Unable not add the product. Null object given.");
        }
        return new ResponseEntity<>(convertFakeStoreProductToProduct(productDto), HttpStatus.OK);
    }

    @Override
    public ResponseEntity<Product> updateProduct(Long id, FakeStoreProductDto fakeStoreProductDto){
        HttpEntity<FakeStoreProductDto> request = new HttpEntity<>(fakeStoreProductDto);
        ResponseEntity<FakeStoreProductDto> response = restTemplate.exchange("https://fakestoreapi.com/products/" + id,
                HttpMethod.PATCH, request, FakeStoreProductDto.class);
        return new ResponseEntity<>(convertFakeStoreProductToProduct(response.getBody()),
                response.getStatusCode());

    }

    @Override
    public ResponseEntity<Product> replaceProduct(Long id, FakeStoreProductDto fakeStoreProductDto){
        HttpEntity<FakeStoreProductDto> request = new HttpEntity<>(fakeStoreProductDto);
        ResponseEntity<FakeStoreProductDto> response = restTemplate.exchange("https://fakestoreapi.com/products/" + id,
                HttpMethod.PUT, request, FakeStoreProductDto.class);
        return  new ResponseEntity<>(convertFakeStoreProductToProduct(response.getBody()),
                response.getStatusCode());
    }

    @Override
    public ResponseEntity<Product> deleteProduct(Long id){
        ResponseEntity<FakeStoreProductDto> response = restTemplate.exchange("https://fakestoreapi.com/products/" + id, HttpMethod.DELETE, null, FakeStoreProductDto.class);
        return new ResponseEntity<>(convertFakeStoreProductToProduct(response.getBody()),
                response.getStatusCode());
    }



}
