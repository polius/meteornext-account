CREATE TABLE `accounts` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(191) NOT NULL,
  `password` VARCHAR(191) NOT NULL,
  `last_login` DATETIME NULL,
  `ip` VARCHAR(191) NULL,
  `disabled` TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  `deleted` TINYINT(1) UNSIGNED NOT NULL DEFAULT '0',
  `created_at` DATETIME NOT NULL,
  `deleted_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `accounts_mfa` (
  `account_id` INT UNSIGNED NOT NULL,
  `2fa_hash` VARCHAR(191) NULL,
  `webauthn_ukey` TEXT NULL,
  `webauthn_pub_key` TEXT NULL,
  `webauthn_credential_id` TEXT NULL,
  `webauthn_sign_count` INT UNSIGNED NULL,
  `webauthn_rp_id` TEXT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`account_id`),
  FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `licenses` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `servers` INT UNSIGNED NOT NULL,
  `price` DOUBLE NOT NULL,
  `code` VARCHAR(191) NULL,
  `code_expiration` DATETIME NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `account_licenses` (
  `account_id` INT UNSIGNED NOT NULL,
  `license_id` INT UNSIGNED NOT NULL,
  `purchase_date` DATETIME NOT NULL,
  `expiration_date` DATETIME NULL,
  `status` ENUM('pending','active','expired') NOT NULL,
  PRIMARY KEY (`account_id`, `license_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;

CREATE TABLE `license_pricing` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `base` DOUBLE NOT NULL,
  `server` DOUBLE NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;