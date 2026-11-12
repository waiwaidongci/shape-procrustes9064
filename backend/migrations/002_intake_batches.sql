
CREATE TABLE intake_batches (
	id SERIAL NOT NULL,
	token VARCHAR(36) NOT NULL,
	collection_id INTEGER NOT NULL,
	actor VARCHAR(160) NOT NULL,
	base_fingerprint VARCHAR(64) NOT NULL,
	rows JSON NOT NULL,
	summary JSON NOT NULL,
	status VARCHAR(20) NOT NULL,
	result JSON NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	confirmed_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id),
	UNIQUE (token),
	FOREIGN KEY(collection_id) REFERENCES shape_collections (id)
)

;
