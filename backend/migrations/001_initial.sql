
CREATE TABLE audits (
	id SERIAL NOT NULL,
	actor VARCHAR(160) NOT NULL,
	action VARCHAR(180) NOT NULL,
	status_code INTEGER NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (id)
)

;


CREATE TABLE templates (
	id SERIAL NOT NULL,
	code VARCHAR(40) NOT NULL,
	name VARCHAR(100) NOT NULL,
	labels JSON NOT NULL,
	points JSON NOT NULL,
	convention VARCHAR(1200) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (code)
)

;


CREATE TABLE users (
	id SERIAL NOT NULL,
	email VARCHAR(160) NOT NULL,
	name VARCHAR(80) NOT NULL,
	role VARCHAR(20) NOT NULL,
	password_hash VARCHAR(250) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (email)
)

;


CREATE TABLE shape_collections (
	id SERIAL NOT NULL,
	code VARCHAR(40) NOT NULL,
	name VARCHAR(140) NOT NULL,
	template_id INTEGER NOT NULL,
	protocol VARCHAR(1200) NOT NULL,
	source_file VARCHAR(140) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (code),
	FOREIGN KEY(template_id) REFERENCES templates (id)
)

;


CREATE TABLE alignment_runs (
	id SERIAL NOT NULL,
	name VARCHAR(140) NOT NULL,
	collection_id INTEGER NOT NULL,
	retained INTEGER NOT NULL,
	tolerance DOUBLE PRECISION NOT NULL,
	status VARCHAR(20) NOT NULL,
	snapshot JSON NOT NULL,
	result JSON NOT NULL,
	error VARCHAR(600) NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (name),
	FOREIGN KEY(collection_id) REFERENCES shape_collections (id)
)

;


CREATE TABLE shape_specimens (
	id SERIAL NOT NULL,
	collection_id INTEGER NOT NULL,
	code VARCHAR(50) NOT NULL,
	name VARCHAR(100) NOT NULL,
	points JSON NOT NULL,
	source_note VARCHAR(300) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (collection_id, code),
	FOREIGN KEY(collection_id) REFERENCES shape_collections (id)
)

;


CREATE TABLE inspection_notes (
	id SERIAL NOT NULL,
	name VARCHAR(140) NOT NULL,
	run_id INTEGER NOT NULL,
	specimen_id INTEGER NOT NULL,
	protocol VARCHAR(2000) NOT NULL,
	status VARCHAR(20) NOT NULL,
	reviewer_note VARCHAR(1000) NOT NULL,
	reviewed_by VARCHAR(140) NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (name),
	FOREIGN KEY(run_id) REFERENCES alignment_runs (id),
	FOREIGN KEY(specimen_id) REFERENCES shape_specimens (id)
)

;
