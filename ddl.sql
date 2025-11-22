CREATE TABLE users (
	id text NOT NULL,
	username text NOT NULL,
	email text NOT NULL,
	"password" text NOT NULL,
	created_at timestamptz DEFAULT now() NULL,
	updated_at timestamptz NULL,
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_password_key UNIQUE (password),
	CONSTRAINT users_pkey PRIMARY KEY (id),
	CONSTRAINT users_username_key UNIQUE (username)
);

CREATE TABLE tasks (
	id text NOT NULL,
	user_id text NOT NULL,
	title text NOT NULL,
	description text NULL,
	created_at timestamptz DEFAULT now() NULL,
	updated_at timestamptz NULL,
	CONSTRAINT tasks_pkey PRIMARY KEY (id)
);
