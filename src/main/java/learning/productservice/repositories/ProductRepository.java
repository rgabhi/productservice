package learning.productservice.repositories;

import learning.productservice.models.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // returns nulls if no match - hence add Optional
    @Override
    Optional<Product> findById(Long Id);
    List<Product>  findAll();
}
