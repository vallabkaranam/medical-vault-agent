-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Create the main results table
create table compliance_results (
  id uuid default uuid_generate_v4() primary key,
  record_id uuid not null,
  session_id text,
  standard text not null,
  
  -- JSONB columns for flexible schema storage
  transcription jsonb not null,
  translation jsonb not null,
  standardization jsonb not null,
  
  image_url text,
  processed_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create an index on session_id for fast lookups
create index idx_compliance_results_session_id on compliance_results(session_id);

-- Create Storage Bucket (if not exists)
insert into storage.buckets (id, name, public) 
values ('vaccine-records', 'vaccine-records', true)
on conflict (id) do nothing;

-- Storage Policy: Allow public read access
create policy "Public Access"
  on storage.objects for select
  using ( bucket_id = 'vaccine-records' );

-- Storage Policy: Allow authenticated uploads (or public for demo)
create policy "Public Upload"
  on storage.objects for insert
  with check ( bucket_id = 'vaccine-records' );
