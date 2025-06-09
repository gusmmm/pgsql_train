-- Enhanced schema for scientific paper extraction and organization
-- This script creates comprehensive tables to store medical research paper data
-- with enhanced metadata, statistical information, and key findings

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Enhanced Papers table (main entity with medical paper specifics)
CREATE TABLE IF NOT EXISTS papers (
    id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT[] NOT NULL DEFAULT '{}', -- Legacy field for backward compatibility
    journal TEXT,
    publication_date TEXT,
    doi TEXT,
    volume TEXT,
    issue TEXT,
    pages TEXT,
    abstract TEXT,
    keywords TEXT[] NOT NULL DEFAULT '{}',
    source_file TEXT NOT NULL,
    
    -- Enhanced fields for medical papers
    paper_type TEXT DEFAULT 'research_article',
    study_design TEXT,
    medical_specialty TEXT,
    study_population TEXT,
    study_period TEXT,
    funding_sources TEXT[] NOT NULL DEFAULT '{}',
    conflict_of_interest TEXT,
    data_availability TEXT,
    ethics_approval TEXT,
    registration_number TEXT,
    supplemental_materials TEXT[] NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Authors table (detailed author information)
CREATE TABLE IF NOT EXISTS authors (
    id BIGINT PRIMARY KEY,
    paper_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    orcid TEXT,
    affiliations TEXT[] NOT NULL DEFAULT '{}',
    is_corresponding BOOLEAN DEFAULT FALSE,
    sequence INTEGER NOT NULL,
    degrees TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE
);

-- Enhanced Sections table (paper content divided into sections)
CREATE TABLE IF NOT EXISTS sections (
    id BIGINT PRIMARY KEY,
    paper_id BIGINT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    section_type TEXT NOT NULL,
    level INTEGER NOT NULL,
    parent_id BIGINT,
    sequence INTEGER NOT NULL,
    
    -- Enhanced fields
    word_count INTEGER DEFAULT 0,
    has_subsections BOOLEAN DEFAULT FALSE,
    statistical_content BOOLEAN DEFAULT FALSE,
    methodology_description BOOLEAN DEFAULT FALSE,
    contains_citations INTEGER DEFAULT 0,
    key_findings TEXT[] NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES sections (id) ON DELETE SET NULL
);

-- Enhanced Tables table (tables extracted from papers)
CREATE TABLE IF NOT EXISTS tables (
    id BIGINT PRIMARY KEY,
    paper_id BIGINT NOT NULL,
    section_id BIGINT,
    caption TEXT,
    content TEXT NOT NULL,
    data JSONB,
    sequence INTEGER NOT NULL,
    
    -- Enhanced fields
    table_type TEXT DEFAULT 'data',
    column_headers TEXT[] NOT NULL DEFAULT '{}',
    row_count INTEGER DEFAULT 0,
    column_count INTEGER DEFAULT 0,
    contains_statistics BOOLEAN DEFAULT FALSE,
    patient_data BOOLEAN DEFAULT FALSE,
    footnotes TEXT[] NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections (id) ON DELETE SET NULL
);

-- Enhanced Images table (images extracted from papers)
CREATE TABLE IF NOT EXISTS images (
    id BIGINT PRIMARY KEY,
    paper_id BIGINT NOT NULL,
    section_id BIGINT,
    caption TEXT,
    file_path TEXT NOT NULL,
    alt_text TEXT,
    width INTEGER,
    height INTEGER,
    sequence INTEGER NOT NULL,
    
    -- Enhanced fields
    image_type TEXT DEFAULT 'figure',
    figure_number TEXT,
    is_embedded BOOLEAN DEFAULT FALSE,
    content_hash TEXT,
    contains_data_visualization BOOLEAN DEFAULT FALSE,
    medical_imaging BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections (id) ON DELETE SET NULL
);

-- Statistical data table (captures statistical information from medical papers)
CREATE TABLE IF NOT EXISTS statistical_data (
    id BIGINT PRIMARY KEY,
    paper_id BIGINT NOT NULL,
    section_id BIGINT,
    statistic_type TEXT NOT NULL,
    value DECIMAL,
    value_text TEXT NOT NULL,
    confidence_interval TEXT,
    p_value DECIMAL,
    context TEXT NOT NULL,
    variable_name TEXT,
    comparison_groups TEXT[] NOT NULL DEFAULT '{}',
    sample_size INTEGER,
    sequence INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections (id) ON DELETE SET NULL
);

-- Key findings table (captures key findings and outcomes)
CREATE TABLE IF NOT EXISTS key_findings (
    id BIGINT PRIMARY KEY,
    paper_id BIGINT NOT NULL,
    section_id BIGINT,
    finding_text TEXT NOT NULL,
    finding_type TEXT NOT NULL,
    statistical_significance BOOLEAN,
    clinical_significance TEXT,
    associated_statistics BIGINT[] NOT NULL DEFAULT '{}',
    confidence_level TEXT,
    sequence INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections (id) ON DELETE SET NULL
);

-- References table (references cited in papers)
CREATE TABLE IF NOT EXISTS "references" (
    id BIGINT PRIMARY KEY,
    paper_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    doi TEXT,
    sequence INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE
);

-- Citations table (in-text citations)
CREATE TABLE IF NOT EXISTS citations (
    id BIGINT PRIMARY KEY,
    paper_id BIGINT NOT NULL,
    section_id BIGINT NOT NULL,
    reference_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    context TEXT,
    sequence INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections (id) ON DELETE CASCADE,
    FOREIGN KEY (reference_id) REFERENCES "references" (id) ON DELETE CASCADE
);

-- Create indexes for performance optimization

-- Basic foreign key indexes
CREATE INDEX IF NOT EXISTS idx_authors_paper_id ON authors(paper_id);
CREATE INDEX IF NOT EXISTS idx_sections_paper_id ON sections(paper_id);
CREATE INDEX IF NOT EXISTS idx_tables_paper_id ON tables(paper_id);
CREATE INDEX IF NOT EXISTS idx_images_paper_id ON images(paper_id);
CREATE INDEX IF NOT EXISTS idx_statistical_data_paper_id ON statistical_data(paper_id);
CREATE INDEX IF NOT EXISTS idx_key_findings_paper_id ON key_findings(paper_id);
CREATE INDEX IF NOT EXISTS idx_references_paper_id ON "references"(paper_id);
CREATE INDEX IF NOT EXISTS idx_citations_paper_id ON citations(paper_id);

-- Section hierarchy indexes
CREATE INDEX IF NOT EXISTS idx_sections_parent_id ON sections(parent_id);
CREATE INDEX IF NOT EXISTS idx_sections_level ON sections(level);

-- Sequence indexes for ordering
CREATE INDEX IF NOT EXISTS idx_sections_sequence ON sections(paper_id, sequence);
CREATE INDEX IF NOT EXISTS idx_tables_sequence ON tables(paper_id, sequence);
CREATE INDEX IF NOT EXISTS idx_images_sequence ON images(paper_id, sequence);
CREATE INDEX IF NOT EXISTS idx_statistical_data_sequence ON statistical_data(paper_id, sequence);
CREATE INDEX IF NOT EXISTS idx_key_findings_sequence ON key_findings(paper_id, sequence);

-- Enhanced search indexes
CREATE INDEX IF NOT EXISTS idx_papers_paper_type ON papers(paper_type);
CREATE INDEX IF NOT EXISTS idx_papers_study_design ON papers(study_design);
CREATE INDEX IF NOT EXISTS idx_papers_medical_specialty ON papers(medical_specialty);
CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi);
CREATE INDEX IF NOT EXISTS idx_sections_section_type ON sections(section_type);
CREATE INDEX IF NOT EXISTS idx_statistical_data_type ON statistical_data(statistic_type);
CREATE INDEX IF NOT EXISTS idx_key_findings_type ON key_findings(finding_type);

-- Content type indexes
CREATE INDEX IF NOT EXISTS idx_tables_type ON tables(table_type);
CREATE INDEX IF NOT EXISTS idx_images_type ON images(image_type);
CREATE INDEX IF NOT EXISTS idx_sections_statistical_content ON sections(statistical_content);
CREATE INDEX IF NOT EXISTS idx_tables_contains_statistics ON tables(contains_statistics);
CREATE INDEX IF NOT EXISTS idx_images_data_visualization ON images(contains_data_visualization);

-- Author indexes
CREATE INDEX IF NOT EXISTS idx_authors_name ON authors(name);
CREATE INDEX IF NOT EXISTS idx_authors_last_name ON authors(last_name);
CREATE INDEX IF NOT EXISTS idx_authors_orcid ON authors(orcid);
CREATE INDEX IF NOT EXISTS idx_authors_corresponding ON authors(is_corresponding);

-- Full-text search indexes using trigram similarity
CREATE INDEX IF NOT EXISTS idx_papers_title_trgm ON papers USING GIN (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_papers_abstract_trgm ON papers USING GIN (abstract gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_sections_content_trgm ON sections USING GIN (content gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_sections_title_trgm ON sections USING GIN (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_key_findings_text_trgm ON key_findings USING GIN (finding_text gin_trgm_ops);

-- Array indexes for efficient searching
CREATE INDEX IF NOT EXISTS idx_papers_keywords_gin ON papers USING GIN (keywords);
CREATE INDEX IF NOT EXISTS idx_papers_funding_sources_gin ON papers USING GIN (funding_sources);
CREATE INDEX IF NOT EXISTS idx_authors_affiliations_gin ON authors USING GIN (affiliations);
CREATE INDEX IF NOT EXISTS idx_authors_degrees_gin ON authors USING GIN (degrees);
CREATE INDEX IF NOT EXISTS idx_statistical_data_groups_gin ON statistical_data USING GIN (comparison_groups);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_papers_type_specialty ON papers(paper_type, medical_specialty);
CREATE INDEX IF NOT EXISTS idx_sections_paper_type ON sections(paper_id, section_type);
CREATE INDEX IF NOT EXISTS idx_statistical_data_paper_section ON statistical_data(paper_id, section_id);

-- Trigger function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for all tables
CREATE TRIGGER update_papers_timestamp BEFORE UPDATE ON papers
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER update_authors_timestamp BEFORE UPDATE ON authors
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER update_sections_timestamp BEFORE UPDATE ON sections
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER update_tables_timestamp BEFORE UPDATE ON tables
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER update_images_timestamp BEFORE UPDATE ON images
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER update_statistical_data_timestamp BEFORE UPDATE ON statistical_data
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER update_key_findings_timestamp BEFORE UPDATE ON key_findings
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER update_references_timestamp BEFORE UPDATE ON "references"
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

CREATE TRIGGER update_citations_timestamp BEFORE UPDATE ON citations
    FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

-- Function to automatically calculate word count for sections
CREATE OR REPLACE FUNCTION calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    NEW.word_count = array_length(string_to_array(trim(NEW.content), ' '), 1);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update word count
CREATE TRIGGER calculate_section_word_count 
    BEFORE INSERT OR UPDATE OF content ON sections
    FOR EACH ROW EXECUTE FUNCTION calculate_word_count();

-- Function to detect statistical content in sections
CREATE OR REPLACE FUNCTION detect_statistical_content()
RETURNS TRIGGER AS $$
BEGIN
    -- Simple heuristic to detect statistical content
    NEW.statistical_content = (
        NEW.content ~* '(p\s*[<>=]\s*0\.\d+|confidence\s+interval|odds\s+ratio|hazard\s+ratio|statistical|significance|analysis)' OR
        NEW.title ~* '(statistical|analysis|results)'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically detect statistical content
CREATE TRIGGER detect_section_statistical_content 
    BEFORE INSERT OR UPDATE OF content, title ON sections
    FOR EACH ROW EXECUTE FUNCTION detect_statistical_content();

-- Views for common queries

-- View for complete paper information with author details
CREATE OR REPLACE VIEW paper_details AS
SELECT 
    p.*,
    array_agg(DISTINCT a.name ORDER BY a.sequence) as author_names,
    array_agg(DISTINCT a.email) FILTER (WHERE a.email IS NOT NULL) as author_emails,
    string_agg(DISTINCT a.name, '; ' ORDER BY a.sequence) as authors_formatted
FROM papers p
LEFT JOIN authors a ON p.id = a.paper_id
GROUP BY p.id;

-- View for papers with statistical content
CREATE OR REPLACE VIEW papers_with_statistics AS
SELECT DISTINCT
    p.*,
    COUNT(sd.id) as statistical_data_count,
    COUNT(kf.id) as key_findings_count,
    COUNT(s.id) FILTER (WHERE s.statistical_content = true) as statistical_sections_count
FROM papers p
LEFT JOIN statistical_data sd ON p.id = sd.paper_id
LEFT JOIN key_findings kf ON p.id = kf.paper_id
LEFT JOIN sections s ON p.id = s.paper_id
GROUP BY p.id;

-- View for section hierarchy
CREATE OR REPLACE VIEW section_hierarchy AS
WITH RECURSIVE section_tree AS (
    -- Base case: top-level sections
    SELECT 
        id, paper_id, title, section_type, level, parent_id, sequence,
        title as path,
        0 as depth
    FROM sections 
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive case: child sections
    SELECT 
        s.id, s.paper_id, s.title, s.section_type, s.level, s.parent_id, s.sequence,
        st.path || ' > ' || s.title as path,
        st.depth + 1 as depth
    FROM sections s
    JOIN section_tree st ON s.parent_id = st.id
)
SELECT * FROM section_tree ORDER BY paper_id, sequence;

-- Comments on tables and important columns
COMMENT ON TABLE papers IS 'Main table storing scientific paper metadata with enhanced fields for medical research papers';
COMMENT ON TABLE authors IS 'Detailed author information with affiliations and credentials';
COMMENT ON TABLE sections IS 'Hierarchical sections of papers with enhanced metadata and automatic content analysis';
COMMENT ON TABLE statistical_data IS 'Statistical information extracted from papers including p-values, confidence intervals, etc.';
COMMENT ON TABLE key_findings IS 'Key findings and outcomes identified in papers';
COMMENT ON TABLE tables IS 'Tables from papers with enhanced metadata for medical research data';
COMMENT ON TABLE images IS 'Images and figures from papers with classification and metadata';

COMMENT ON COLUMN papers.paper_type IS 'Type of paper: research_article, review, systematic_review, meta_analysis, case_study, etc.';
COMMENT ON COLUMN papers.study_design IS 'Study design: cohort, case_control, rct, observational, etc.';
COMMENT ON COLUMN sections.statistical_content IS 'Automatically detected based on content analysis';
COMMENT ON COLUMN sections.word_count IS 'Automatically calculated on insert/update';
COMMENT ON COLUMN statistical_data.statistic_type IS 'Type of statistic: odds_ratio, p_value, confidence_interval, hazard_ratio, etc.';
COMMENT ON COLUMN key_findings.finding_type IS 'Type of finding: primary_outcome, secondary_outcome, safety, efficacy, etc.';
