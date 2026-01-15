CREATE TABLE construction_progress (
                                              id BIGSERIAL PRIMARY KEY,
                                              name VARCHAR(50) NOT NULL,
                                              type VARCHAR(255) NOT NULL,
                                              progress VARCHAR(255) NOT NULL,
                                              creator VARCHAR(100) NOT NULL,
                                              created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
                                              updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
                                              deleted_at TIMESTAMP WITHOUT TIME ZONE
);