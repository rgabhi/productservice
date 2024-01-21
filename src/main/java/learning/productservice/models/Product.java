package learning.productservice.models;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
public class Product {
    @Id
    private long id;
    private String title;
    private double price;
    //here category is a non-primitive typo,
    // so handle it with the concept of cardinality,
    @ManyToOne
    private Category category;
    private String description;
    private String imageUrl;
}
