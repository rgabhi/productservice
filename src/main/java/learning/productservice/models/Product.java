package learning.productservice.models;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.io.Serializable;

@Getter
@Setter
@Entity
public class Product extends BaseModel implements Serializable {
    private String title;
    private double price;
    //here category is a non-primitive typo,
    // so handle it with the concept of cardinality,
    @ManyToOne(cascade = {CascadeType.PERSIST, CascadeType.MERGE}, fetch = FetchType.EAGER)
    private Category category;
    private String description;
    private String imageUrl;
}
