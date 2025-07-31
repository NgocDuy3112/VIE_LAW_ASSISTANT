FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

COPY UserServiceApi/UserServiceApi.csproj ./UserServiceApi/
RUN dotnet restore

COPY . .
WORKDIR /src/UserServiceApi
RUN dotnet publish -c Release -o /app/publish --no-restore

# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .

# 👇 Add EF CLI
RUN apt-get update && apt-get install -y libpq-dev curl && \
    dotnet tool install --global dotnet-ef && \
    export PATH="$PATH:/root/.dotnet/tools"

# Copy entrypoint
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENV ASPNETCORE_URLS=http://+:8081
EXPOSE 8081

ENTRYPOINT ["./entrypoint.sh"]