package learning.productservice.services;

import learning.productservice.configs.RedisConfiguration;
import learning.productservice.dtos.FakeStoreProductDto;
import learning.productservice.exceptions.ProductNotCreatedException;
import learning.productservice.exceptions.ProductNotFoundException;
import learning.productservice.models.Category;
import learning.productservice.models.Product;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

@Service("fakeProductService")
public class FakeProductService implements ProductService {
    private RedisTemplate<String, Object> redisTemplate;
    private RestTemplate restTemplate;
    @Autowired
    FakeProductService(RestTemplate restTemplate, RedisTemplate<String, Object> redisTemplate){
        this.restTemplate = restTemplate;
        this.redisTemplate = redisTemplate;
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

    private FakeStoreProductDto convertProductToFakeStoreProduct(Product product){
        FakeStoreProductDto fakeStoreProductDto = new FakeStoreProductDto();
        fakeStoreProductDto.setId(product.getId());
        fakeStoreProductDto.setTitle(product.getTitle());
        fakeStoreProductDto.setPrice(product.getPrice());
        fakeStoreProductDto.setDescription(product.getDescription());
        fakeStoreProductDto.setImage(product.getImageUrl());
        return fakeStoreProductDto;
    }
    @Override
    public Product getSingleProduct(Long id) throws ProductNotFoundException {
        //check if product present in cache
        Product product = (Product) redisTemplate.opsForHash().get("PRODUCTS", "PRODUCT_" + id);
        if(product != null)return product;

        FakeStoreProductDto productDto = restTemplate.getForObject("https://fakestoreapi.com/products/" + id, FakeStoreProductDto.class);
        if(productDto == null){
            throw new ProductNotFoundException("Product with id: "+ id + " not found!");
        }

        // store in cache if not already present
        product = convertFakeStoreProductToProduct(productDto);
        redisTemplate.opsForHash().put("PRODUCTS", "PRODUCT_" + id, product);
        return product;
    }

    @Override
    public List<Product> getAllProducts() throws ProductNotFoundException {
        FakeStoreProductDto[] productDto = restTemplate.getForObject("https://fakestoreapi.com/products/", FakeStoreProductDto[].class);
        List<Product> productList = new ArrayList<>();
        if(productDto == null){
            throw  new ProductNotFoundException("No products to show :(");
        }
        for(FakeStoreProductDto fakeProductDto : productDto){
            productList.add(convertFakeStoreProductToProduct(fakeProductDto));
        }
        return productList;
    }

    @Override
    public  Product addProduct(Product product) throws ProductNotCreatedException {
//        HttpEntity<FakeStoreProductDto> request = new HttpEntity<>(fakeStoreProductDto);
        // dto is not used in service layer,
        // here just being used since FakeStoreProduct has same structure as its dto;
        FakeStoreProductDto fakeStoreProductDto = convertProductToFakeStoreProduct(product);
        FakeStoreProductDto productDto = restTemplate.postForObject("https://fakestoreapi.com/products", fakeStoreProductDto, FakeStoreProductDto.class);
        if(productDto == null){
            throw new ProductNotCreatedException("Unable not add the product. Null object given.");
        }
        return convertFakeStoreProductToProduct(productDto);
    }

    @Override
    public Product updateProduct(Long id, Product product){
        HttpEntity<FakeStoreProductDto> request = new HttpEntity<>(convertProductToFakeStoreProduct(product));
        ResponseEntity<FakeStoreProductDto> response = restTemplate.exchange("https://fakestoreapi.com/products/" + id,
                HttpMethod.PATCH, request, FakeStoreProductDto.class);
        return convertFakeStoreProductToProduct(response.getBody());
    }

    @Override
    public Product replaceProduct(Long id, Product product){
        HttpEntity<FakeStoreProductDto> request = new HttpEntity<>(convertProductToFakeStoreProduct(product));
        ResponseEntity<FakeStoreProductDto> response = restTemplate.exchange("https://fakestoreapi.com/products/" + id,
                HttpMethod.PUT, request, FakeStoreProductDto.class);
        return  convertFakeStoreProductToProduct(response.getBody());
    }

    @Override
    public void deleteProduct(Long id){
        ResponseEntity<FakeStoreProductDto> response = restTemplate.exchange("https://fakestoreapi.com/products/" + id,
                HttpMethod.DELETE, null, FakeStoreProductDto.class);

    }



}
