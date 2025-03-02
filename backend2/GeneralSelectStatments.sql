-- SELECT All Image Assets
SELECT 
    a.StorageLocation
,   ia.Width
,   ia.Height
FROM Asset AS a
JOIN ImageAsset AS ia
    ON ia.ReferenceHash = a.ReferenceHash
WHERE 0=0

-- SELECT All Audio Assets
SELECT 
    a.StorageLocation
,   aa.Duration
FROM Asset AS a
JOIN AudioAsset AS aa
    ON aa.ReferenceHash = a.ReferenceHash
WHERE 0=0

-- SELECT All Video Assets
SELECT 
    a.StorageLocation
,   va.Width
,   va.Height
,   va.Duration
FROM Asset AS a
JOIN VideoAsset AS va
    ON va.ReferenceHash = a.ReferenceHash
WHERE 0=0

-- SELECT All User Saved Assets Hashs
SELECT 
    a.ReferenceHash
FROM Asset AS a
JOIN UserSavedAssets AS usa
    ON usa.ReferenceHash = a.ReferenceHash
WHERE 0=0

-- SELECT All Non Approved User Added Assets
SELECT
    a.ReferenceHash
FROM Asset AS a
JOIN UserAddedAssets AS uaa
    ON uaa.ReferenceHash = a.ReferenceHash
WHERE 0=0
AND uaa.Approved = FALSE

-- SELECT Asset By Hash
SELECT
    a.StorageLocation
FROM Asset AS a
WHERE 0=0
AND a.ReferenceHash = @InputReferenceHash

-- REMOVE expired Caches
DELETE
FROM Cache AS c
WHERE NOW() >= c.TTL

-- SELECT Assets with tag
SELECT
    a.*
FROM Asset AS a
JOIN Tags AS t
    ON t.ReferenceHash = a.ReferenceHash
WHERE 0=0
AND t.Tag = @InputTag
