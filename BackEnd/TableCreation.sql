CREATE TABLE `Asset`(
    `Id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `ReferenceHash` VARCHAR(255) NOT NULL,
    `Name` VARCHAR(255) NOT NULL,
    `Type` VARCHAR(255) NOT NULL,
    `StorageLocation` VARCHAR(255) NOT NULL
);
ALTER TABLE
    `Asset` ADD UNIQUE `asset_referencehash_unique`(`ReferenceHash`);
CREATE TABLE `ImageAsset`(
    `Id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `ReferenceHash` VARCHAR(255) NOT NULL,
    `Width` SMALLINT NOT NULL,
    `Height` SMALLINT NOT NULL
);
CREATE TABLE `AudioAsset`(
    `Id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `ReferenceHash` VARCHAR(255) NOT NULL,
    `Duration` DOUBLE NOT NULL
);
CREATE TABLE `VideoAsset`(
    `Id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `ReferenceHash` VARCHAR(255) NOT NULL,
    `Width` SMALLINT NOT NULL,
    `Height` SMALLINT NOT NULL,
    `Duration` DOUBLE NOT NULL
);
CREATE TABLE `Tags`(
    `Id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `ReferenceHash` VARCHAR(255) NOT NULL,
    `Tag` VARCHAR(255) NOT NULL
);
CREATE TABLE `API`(
    `Id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `Name` VARCHAR(255) NOT NULL,
    `URL` VARCHAR(255) NOT NULL
);
CREATE TABLE `APIEndpoints`(
    `Id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `APIID` INT NOT NULL,
    `APIName` VARCHAR(255) NOT NULL,
    `Endpoint` VARCHAR(255) NOT NULL
);
CREATE TABLE `User`(
    `Id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `Username` VARCHAR(255) NOT NULL,
    `HashedPassword` VARCHAR(255) NOT NULL
);
CREATE TABLE `UserSavedAssets`(
    `UserId` INT UNSIGNED NOT NULL,
    `ReferenceHash` VARCHAR(255) NOT NULL,
    PRIMARY KEY(`UserId`, `ReferenceHash`)
);
CREATE TABLE `UserAddedAssets`(
    `UserId` INT UNSIGNED NOT NULL,
    `ReferenceHash` VARCHAR(255) NOT NULL,
    `Approved` BOOLEAN NOT NULL,
    PRIMARY KEY(`UserId`, `ReferenceHash`)
);
CREATE TABLE `Cache`(
    `Id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `AssetHash` VARCHAR(255) NOT NULL,
    `OriginalLocation` VARCHAR(255) NOT NULL,
    `TimeOfCreation` DATETIME NOT NULL,
    `TTL` DATETIME NOT NULL
);
ALTER TABLE
    `APIEndpoints` ADD CONSTRAINT `apiendpoints_apiid_foreign` FOREIGN KEY(`APIID`) REFERENCES `API`(`Id`);
ALTER TABLE
    `Asset` ADD CONSTRAINT `asset_storagelocation_foreign` FOREIGN KEY(`StorageLocation`) REFERENCES `APIEndpoints`(`Endpoint`);
ALTER TABLE
    `Cache` ADD CONSTRAINT `cache_assethash_foreign` FOREIGN KEY(`AssetHash`) REFERENCES `Asset`(`ReferenceHash`);
ALTER TABLE
    `Asset` ADD CONSTRAINT `asset_referencehash_foreign` FOREIGN KEY(`ReferenceHash`) REFERENCES `UserAddedAssets`(`ReferenceHash`);
ALTER TABLE
    `AudioAsset` ADD CONSTRAINT `audioasset_referencehash_foreign` FOREIGN KEY(`ReferenceHash`) REFERENCES `Asset`(`ReferenceHash`);
ALTER TABLE
    `APIEndpoints` ADD CONSTRAINT `apiendpoints_apiname_foreign` FOREIGN KEY(`APIName`) REFERENCES `API`(`Name`);
ALTER TABLE
    `User` ADD CONSTRAINT `user_id_foreign` FOREIGN KEY(`Id`) REFERENCES `UserAddedAssets`(`UserId`);
ALTER TABLE
    `Tags` ADD CONSTRAINT `tags_referencehash_foreign` FOREIGN KEY(`ReferenceHash`) REFERENCES `Asset`(`ReferenceHash`);
ALTER TABLE
    `Asset` ADD CONSTRAINT `asset_referencehash_foreign` FOREIGN KEY(`ReferenceHash`) REFERENCES `UserSavedAssets`(`ReferenceHash`);
ALTER TABLE
    `User` ADD CONSTRAINT `user_id_foreign` FOREIGN KEY(`Id`) REFERENCES `UserSavedAssets`(`UserId`);
ALTER TABLE
    `VideoAsset` ADD CONSTRAINT `videoasset_width_foreign` FOREIGN KEY(`Width`) REFERENCES `Asset`(`ReferenceHash`);
ALTER TABLE
    `ImageAsset` ADD CONSTRAINT `imageasset_referencehash_foreign` FOREIGN KEY(`ReferenceHash`) REFERENCES `Asset`(`ReferenceHash`);